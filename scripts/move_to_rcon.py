from __future__ import annotations

import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from factorio_rcon_common import run_rcon_command


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python scripts/move_to_rcon.py <x> <y>", file=sys.stderr)
        return 1

    try:
        target_x = float(sys.argv[1])
        target_y = float(sys.argv[2])
    except ValueError:
        print("x and y must be numeric", file=sys.stderr)
        return 1

    walk_duration_seconds = float(os.environ.get("FACTORIO_WALK_STEP_SECONDS", "0.25"))

    factorio_user_dir = Path(
        os.environ.get(
            "FACTORIO_USER_DATA_DIR",
            str(
                Path.home()
                / ".local/share/Steam/steamapps/compatdata/427520/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio"
            ),
        )
    )

    output_dir = factorio_user_dir / "script-output" / "chatgpt"
    result_path = output_dir / "move_to_result.json"
    error_path = output_dir / "move_to_error.txt"
    started_path = output_dir / "move_to_started.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in (result_path, error_path, started_path):
        if path.exists():
            path.unlink()

    command_start = f"/chatgpt-move-step {target_x},{target_y}"
    command_stop = "/chatgpt-stop-walk"

    try:
        run_rcon_command(command_start)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RCON move failed: {exc}", file=sys.stderr)
        return 1

    deadline = time.time() + 1.0
    while time.time() < deadline:
        if result_path.exists():
            print(result_path.read_text(encoding="utf-8").strip())
            return 0

        if error_path.exists():
            error_text = error_path.read_text(encoding="utf-8").strip()
            print(f"move_to error: {error_text}", file=sys.stderr)
            return 1

        if started_path.exists():
            break

        time.sleep(0.05)

    if not started_path.exists() and not result_path.exists():
        print(f"move_to start marker was not created: {started_path}", file=sys.stderr)
        return 1

    time.sleep(walk_duration_seconds)

    try:
        run_rcon_command(command_stop)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RCON move failed during stop: {exc}", file=sys.stderr)
        return 1

    deadline = time.time() + 5.0
    while time.time() < deadline:
        if result_path.exists():
            print(result_path.read_text(encoding="utf-8").strip())
            return 0

        if error_path.exists():
            error_text = error_path.read_text(encoding="utf-8").strip()
            print(f"move_to error: {error_text}", file=sys.stderr)
            return 1

        time.sleep(0.1)

    print(f"move_to result file was not created: {result_path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())