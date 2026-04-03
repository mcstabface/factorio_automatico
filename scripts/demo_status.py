from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_env_check() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        "python scripts/check_factorio_bridge_env.py",
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def _parse_env_summary(stdout_text: str) -> dict[str, object]:
    return json.loads(stdout_text.strip())


def _recommended_commands(summary: dict[str, object]) -> list[str]:
    checks = summary.get("checks", {})
    if not isinstance(checks, dict):
        return ["python scripts/check_factorio_bridge_env.py"]

    rcon_listener = checks.get("rcon_listener", {})
    if not isinstance(rcon_listener, dict) or not rcon_listener.get("ok", False):
        return [
            "bash scripts/start_factorio_headless.sh",
            "source scripts/set_factorio_bridge_env.sh",
            "python scripts/check_factorio_bridge_env.py",
        ]

    return [
        "python scripts/smoke_live_bridge.py",
        "python scripts/run_live_factorio_stream_demo.py",
        "python scripts/run_live_factorio_walk_to_target.py --trace 10 10",
    ]


def main() -> int:
    completed = _run_env_check()

    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)

    if completed.returncode not in (0, 1):
        print("demo status failed: env check command error", file=sys.stderr)
        return 1

    try:
        summary = _parse_env_summary(completed.stdout)
    except json.JSONDecodeError:
        print("demo status failed: env check output was not valid JSON", file=sys.stderr)
        return 1

    overall_ok = bool(summary.get("overall_ok", False))
    recommended = _recommended_commands(summary)

    payload = {
        "overall_ok": overall_ok,
        "recommended_next_commands": recommended,
        "repo_root": summary.get("repo_root"),
    }

    if overall_ok:
        print("demo status: live bridge looks ready", file=sys.stderr)
    else:
        print("demo status: live bridge not ready yet", file=sys.stderr)

    for command in recommended:
        print(f"next: {command}", file=sys.stderr)

    print(json.dumps(payload, indent=2))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())