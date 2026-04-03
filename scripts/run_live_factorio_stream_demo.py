from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_demo_command() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        "python scripts/run_live_factorio_demo.py",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def _parse_summary(stdout_text: str) -> dict[str, object]:
    return json.loads(stdout_text.strip())


def _emit_stream_header(summary: dict[str, object]) -> None:
    starting_position = summary["starting_position"]
    requested_target = summary["requested_target"]
    requested_offset = summary["requested_offset"]

    print("=== Factorio Live Demo ===", file=sys.stderr)
    print(
        (
            f"start=({starting_position['x']:.3f}, {starting_position['y']:.3f}) "
            f"offset=({requested_offset['x']:.3f}, {requested_offset['y']:.3f}) "
            f"target=({requested_target['x']:.3f}, {requested_target['y']:.3f})"
        ),
        file=sys.stderr,
    )


def _emit_stream_footer(summary: dict[str, object]) -> None:
    final_position = summary["final_position"]
    result_status = summary["result_status"]
    steps_taken = summary["steps_taken"]

    print(
        (
            f"result={result_status} "
            f"steps={steps_taken} "
            f"final=({final_position['x']:.3f}, {final_position['y']:.3f})"
        ),
        file=sys.stderr,
    )
    print("=== End Factorio Live Demo ===", file=sys.stderr)


def main() -> int:
    completed = _run_demo_command()

    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)

    if completed.returncode not in (0, 1):
        print("stream demo failed: underlying demo command error", file=sys.stderr)
        return 1

    try:
        summary = _parse_summary(completed.stdout)
    except json.JSONDecodeError:
        print("stream demo failed: underlying demo output was not valid JSON", file=sys.stderr)
        return 1

    _emit_stream_header(summary)
    print(json.dumps(summary, indent=2))
    _emit_stream_footer(summary)

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())