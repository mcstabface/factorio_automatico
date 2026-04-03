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
    output_path = output_dir / "player_position.json"
    error_path = output_dir / "player_position_error.txt"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in (output_path, error_path):
        if path.exists():
            path.unlink()

    command = "/chatgpt-get-position"

    try:
        run_rcon_command(command)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RCON probe failed: {exc}", file=sys.stderr)
        return 1

    deadline = time.time() + 5.0
    while time.time() < deadline:
        if output_path.exists():
            print(output_path.read_text(encoding="utf-8").strip())
            return 0

        if error_path.exists():
            error_text = error_path.read_text(encoding="utf-8").strip()
            print(f"position probe error: {error_text}", file=sys.stderr)
            return 1

        time.sleep(0.1)

    print(
        f"position output file was not created: {output_path}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())