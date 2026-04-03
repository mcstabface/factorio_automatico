from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.world_state import Position
from integrations.factorio.factorio_client import FactorioClient


DEFAULT_TOLERANCE = 0.75
DEFAULT_MAX_STEPS = 12
DEFAULT_MIN_PROGRESS = 0.05
TRACE_FLAG = "--trace"


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


def _format_position(position: Position) -> str:
    return f"({position.x:.3f}, {position.y:.3f})"


def _emit_trace(trace_sink: Callable[[str], None] | None, message: str) -> None:
    if trace_sink is None:
        return
    trace_sink(message)


def _parse_args(argv: list[str]) -> tuple[bool, float, float, float, int, float] | None:
    trace_enabled = False
    positional_args: list[str] = []

    for arg in argv[1:]:
        if arg == TRACE_FLAG:
            trace_enabled = True
            continue
        positional_args.append(arg)

    if len(positional_args) not in (2, 3, 4, 5):
        print(
            (
                "usage: python scripts/run_live_factorio_walk_to_target.py "
                "[--trace] <x> <y> [tolerance] [max_steps] [min_progress]"
            ),
            file=sys.stderr,
        )
        return None

    try:
        target_x = float(positional_args[0])
        target_y = float(positional_args[1])
        tolerance = (
            float(positional_args[2])
            if len(positional_args) >= 3
            else DEFAULT_TOLERANCE
        )
        max_steps = (
            int(positional_args[3])
            if len(positional_args) >= 4
            else DEFAULT_MAX_STEPS
        )
        min_progress = (
            float(positional_args[4])
            if len(positional_args) >= 5
            else DEFAULT_MIN_PROGRESS
        )
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

    return trace_enabled, target_x, target_y, tolerance, max_steps, min_progress


def run_walk_to_target(
    *,
    client: FactorioClient,
    target_position: Position,
    tolerance: float = DEFAULT_TOLERANCE,
    max_steps: int = DEFAULT_MAX_STEPS,
    min_progress: float = DEFAULT_MIN_PROGRESS,
    trace_sink: Callable[[str], None] | None = None,
) -> dict[str, object]:
    initial_position = client.get_player_position()
    current_position = initial_position
    initial_distance = _distance(current_position, target_position)

    step_history: list[dict[str, object]] = []

    _emit_trace(
        trace_sink,
        (
            f"walk start: from {_format_position(initial_position)} "
            f"to {_format_position(target_position)} "
            f"(distance={initial_distance:.3f}, tolerance={tolerance:.3f})"
        ),
    )

    if initial_distance <= tolerance:
        _emit_trace(trace_sink, "walk stop: already within tolerance")
        return {
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

        _emit_trace(
            trace_sink,
            (
                f"step {step_index}: before={_format_position(before_position)} "
                f"after={_format_position(after_position)} "
                f"remaining={after_distance:.3f} progress={progress_distance:.3f}"
            ),
        )

        current_position = after_position

        if after_distance <= tolerance:
            status = "target_reached"
            _emit_trace(trace_sink, f"walk stop: target reached in {step_index} step(s)")
            break

        if progress_distance < min_progress:
            status = "stuck_no_progress"
            _emit_trace(
                trace_sink,
                (
                    f"walk stop: stuck after {step_index} step(s) "
                    f"(progress={progress_distance:.3f} < min_progress={min_progress:.3f})"
                ),
            )
            break
    else:
        _emit_trace(trace_sink, f"walk stop: max steps reached ({max_steps})")

    final_distance = _distance(current_position, target_position)

    return {
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


def main() -> int:
    parsed_args = _parse_args(sys.argv)
    if parsed_args is None:
        return 1

    trace_enabled, target_x, target_y, tolerance, max_steps, min_progress = parsed_args

    client = FactorioClient()
    target_position = Position(x=target_x, y=target_y)

    summary = run_walk_to_target(
        client=client,
        target_position=target_position,
        tolerance=tolerance,
        max_steps=max_steps,
        min_progress=min_progress,
        trace_sink=(lambda message: print(message, file=sys.stderr)) if trace_enabled else None,
    )

    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] in {"target_reached", "already_within_tolerance"} else 1


if __name__ == "__main__":
    raise SystemExit(main())