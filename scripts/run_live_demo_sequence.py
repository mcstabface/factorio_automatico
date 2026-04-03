from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    smoke_command = "python scripts/smoke_live_bridge.py"
    stream_demo_command = "python scripts/run_live_factorio_stream_demo.py"

    print("sequence: starting live smoke check", file=sys.stderr)
    smoke_result = _run_command(smoke_command)

    if smoke_result.stdout.strip():
        print(smoke_result.stdout.strip(), file=sys.stderr)
    if smoke_result.stderr.strip():
        print(smoke_result.stderr.strip(), file=sys.stderr)

    if smoke_result.returncode != 0:
        print("sequence: stopped because smoke check failed", file=sys.stderr)
        return 1

    print("sequence: smoke check passed", file=sys.stderr)
    print("sequence: starting stream demo", file=sys.stderr)

    stream_result = _run_command(stream_demo_command)

    if stream_result.stderr.strip():
        print(stream_result.stderr.strip(), file=sys.stderr)

    if stream_result.stdout.strip():
        print(stream_result.stdout.strip())

    if stream_result.returncode not in (0, 1):
        print("sequence: stream demo command error", file=sys.stderr)
        return 1

    if stream_result.returncode == 0:
        print("sequence: stream demo completed successfully", file=sys.stderr)
    else:
        print("sequence: stream demo completed with bounded failure", file=sys.stderr)

    return stream_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())