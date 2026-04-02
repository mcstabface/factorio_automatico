from __future__ import annotations

import json
import subprocess
import sys


def _run_command(command: str, timeout_seconds: float = 10.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )


def _parse_position(output_text: str) -> dict[str, float]:
    payload = json.loads(output_text.strip())
    return {
        "x": float(payload["x"]),
        "y": float(payload["y"]),
    }


def main() -> int:
    read_command = "python scripts/get_player_position.py"
    move_command = "python scripts/move_to_rcon.py 10 10"

    before_result = _run_command(read_command)
    if before_result.returncode != 0:
        print("live bridge smoke failed during initial read", file=sys.stderr)
        print(before_result.stderr.strip(), file=sys.stderr)
        return 1

    before_position = _parse_position(before_result.stdout)

    move_result = _run_command(move_command)
    if move_result.returncode != 0:
        print("live bridge smoke failed during move", file=sys.stderr)
        print(move_result.stderr.strip(), file=sys.stderr)
        return 1

    move_position = _parse_position(move_result.stdout)

    after_result = _run_command(read_command)
    if after_result.returncode != 0:
        print("live bridge smoke failed during final read", file=sys.stderr)
        print(after_result.stderr.strip(), file=sys.stderr)
        return 1

    after_position = _parse_position(after_result.stdout)

    summary = {
        "before": before_position,
        "move_result": move_position,
        "after": after_position,
        "delta": {
            "x": after_position["x"] - before_position["x"],
            "y": after_position["y"] - before_position["y"],
        },
    }

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())