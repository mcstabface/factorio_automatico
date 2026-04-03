from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.world_state import Position
from integrations.factorio.factorio_client import FactorioClient


DEFAULT_TOLERANCE = 0.75
DEFAULT_MAX_STEPS = 12
DEFAULT_MIN_PROGRESS = 0.05


def _to_plain_value(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, tuple):
        return [_to_plain_value(item) for item in value]

    if isinstance(value, list):
        return [_to_plain_value(item) for item in value]

    if isinstance(value, dict):
        return {key: _to_plain_value(item) for key, item in value.items()}

    return value


def _distance(a: Position, b: Position) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)


def _parse_args(argv: list[str]) -> tuple[float, float, float, int, float] | None:
    if len(argv) not in (3, 4, 5, 6):
        print(
            (
                "usage: python scripts/run_live_factorio_walk_to_target.py "
                "<x> <y> [tolerance] [max_steps] [min_progress]"
            ),
            file=sys.stderr,
        )
        return None

    try:
        target_x = float(argv[1])
        target_y = float(argv[2])
        tolerance = float(argv[3]) if len(argv) >= 4 else DEFAULT_TOLERANCE
        max_steps = int(argv[4]) if len(argv) >= 5 else DEFAULT_MAX_STEPS
        min_progress = float(argv[5]) if len(argv) >= 6 else DEFAULT_MIN_PROGRESS
    except ValueError:
        print(
            "x, y, tolerance, max_steps, and min_progress must be numeric",
            file=sys.stderr,
        )
        return None

    if tolerance < 0.0:
        print("tolerance must be >= 0", file=sys.stderr)
        return None

    if max_steps <= 0:
        print("max_steps must be > 0", file=sys.stderr)
        return None

    if min_progress < 0.0:
        print("min_progress must be >= 0", file=sys.stderr)
        return None

    return target_x, target_y, tolerance, max_steps, min_progress


def main() -> int:
    parsed_args = _parse_args(sys.argv)
    if parsed_args is None:
        return 1

    target_x, target_y, tolerance, max_steps, min_progress = parsed_args

    client = FactorioClient()
    target_position = Position(x=target_x, y=target_y)

    initial_position = client.get_player_position()
    current_position = initial_position
    initial_distance = _distance(current_position, target_position)

    step_history: list[dict[str, object]] = []

    if initial_distance <= tolerance:
        summary = {
            "status": "already_within_tolerance",
            "target_position": _to_plain_value(target_position),
            "tolerance": tolerance,
            "max_steps": max_steps,
            "min_progress": min_progress,
            "initial_position": _to_plain_value(initial_position),
            "final_position": _to_plain_value(current_position),
            "initial_distance": initial_distance,
            "final_distance": initial_distance,
            "steps_taken": 0,
            "step_history": step_history,
        }
        print(json.dumps(summary, indent=2))
        return 0

    status = "max_steps_reached"

    for step_index in range(1, max_steps + 1):
        before_position = current_position
        before_distance = _distance(before_position, target_position)

        move_result = client.move_to(target_position.x, target_position.y)
        after_position = client.get_player_position()
        after_distance = _distance(after_position, target_position)

        progress_distance = before_distance - after_distance

        step_record = {
            "step_index": step_index,
            "before_position": _to_plain_value(before_position),
            "after_position": _to_plain_value(after_position),
            "before_distance": before_distance,
            "after_distance": after_distance,
            "progress_distance": progress_distance,
            "move_result": _to_plain_value(move_result),
        }
        step_history.append(step_record)

        current_position = after_position

        if after_distance <= tolerance:
            status = "target_reached"
            break

        if progress_distance < min_progress:
            status = "stuck_no_progress"
            break

    final_distance = _distance(current_position, target_position)

    summary = {
        "status": status,
        "target_position": _to_plain_value(target_position),
        "tolerance": tolerance,
        "max_steps": max_steps,
        "min_progress": min_progress,
        "initial_position": _to_plain_value(initial_position),
        "final_position": _to_plain_value(current_position),
        "initial_distance": initial_distance,
        "final_distance": final_distance,
        "steps_taken": len(step_history),
        "step_history": step_history,
    }

    print(json.dumps(summary, indent=2))
    return 0 if status in {"target_reached", "already_within_tolerance"} else 1


if __name__ == "__main__":
    raise SystemExit(main())