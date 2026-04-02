from __future__ import annotations

import json
import os
import subprocess
import sys


def _normalize_position_output(raw_output: str) -> dict[str, float]:
    last_line = raw_output.strip().splitlines()[-1].strip()

    try:
        payload = json.loads(last_line)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        if "x" in payload and "y" in payload:
            return {
                "x": float(payload["x"]),
                "y": float(payload["y"]),
            }

        nested_position = payload.get("position")
        if isinstance(nested_position, dict):
            if "x" in nested_position and "y" in nested_position:
                return {
                    "x": float(nested_position["x"]),
                    "y": float(nested_position["y"]),
                }

    x_str, y_str = [part.strip() for part in last_line.split(",", maxsplit=1)]
    return {
        "x": float(x_str),
        "y": float(y_str),
    }


def main() -> int:
    raw_command = os.environ.get("FACTORIO_RAW_POSITION_COMMAND")
    timeout_seconds = float(
        os.environ.get("FACTORIO_RAW_POSITION_TIMEOUT_SECONDS", "2.0")
    )

    if not raw_command:
        print("FACTORIO_RAW_POSITION_COMMAND is not set", file=sys.stderr)
        return 1

    try:
        completed_process = subprocess.run(
            raw_command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"raw position probe failed: {exc}", file=sys.stderr)
        return 1

    if completed_process.returncode != 0:
        stderr_text = completed_process.stderr.strip() or "raw position probe failed"
        print(stderr_text, file=sys.stderr)
        return 1

    stdout_text = completed_process.stdout.strip()
    if not stdout_text:
        print("raw position probe returned no stdout", file=sys.stderr)
        return 1

    try:
        normalized_position = _normalize_position_output(stdout_text)
    except (ValueError, TypeError, IndexError):
        print("unable to parse raw player position output", file=sys.stderr)
        return 1

    print(json.dumps(normalized_position))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())