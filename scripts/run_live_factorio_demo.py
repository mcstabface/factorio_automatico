from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.world_state import Position
from integrations.factorio.factorio_client import FactorioClient
from scripts.run_live_factorio_walk_to_target import (
    DEFAULT_MAX_STEPS,
    DEFAULT_MIN_PROGRESS,
    DEFAULT_TOLERANCE,
    run_walk_to_target,
)


def main() -> int:
    client = FactorioClient()

    before_position = client.get_player_position()
    target_position = Position(
        x=before_position.x + 5.0,
        y=before_position.y + 5.0,
    )

    walk_summary = run_walk_to_target(
        client=client,
        target_position=target_position,
        tolerance=DEFAULT_TOLERANCE,
        max_steps=DEFAULT_MAX_STEPS,
        min_progress=DEFAULT_MIN_PROGRESS,
    )

    summary = {
        "demo_type": "bounded_multi_step_walk",
        "requested_target": {
            "x": target_position.x,
            "y": target_position.y,
        },
        "walk_summary": walk_summary,
    }

    print(json.dumps(summary, indent=2))
    return 0 if walk_summary["status"] in {"target_reached", "already_within_tolerance"} else 1


if __name__ == "__main__":
    raise SystemExit(main())