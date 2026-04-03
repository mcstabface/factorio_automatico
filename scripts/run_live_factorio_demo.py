from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from integrations.factorio.factorio_client import FactorioClient


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


def main() -> int:
    client = FactorioClient()

    before_position = client.get_player_position()

    target_x = before_position.x + 5.0
    target_y = before_position.y + 5.0

    move_result = client.move_to(target_x, target_y)
    after_position = client.get_player_position()

    summary = {
        "before_position": {
            "x": before_position.x,
            "y": before_position.y,
        },
        "requested_target": {
            "x": target_x,
            "y": target_y,
        },
        "move_result": _to_plain_value(move_result),
        "after_position": {
            "x": after_position.x,
            "y": after_position.y,
        },
        "delta": {
            "x": after_position.x - before_position.x,
            "y": after_position.y - before_position.y,
        },
    }

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())