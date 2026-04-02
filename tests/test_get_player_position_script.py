from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "get_player_position.py"
)


def _run_script(raw_command: str | None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()

    if raw_command is None:
        env.pop("FACTORIO_RAW_POSITION_COMMAND", None)
    else:
        env["FACTORIO_RAW_POSITION_COMMAND"] = raw_command

    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_wrapper_normalizes_direct_json_output() -> None:
    result = _run_script(
        """python -c "print('{\\\"x\\\": 7.5, \\\"y\\\": -2.0}')" """
    )

    assert result.returncode == 0
    assert result.stdout.strip() == '{"x": 7.5, "y": -2.0}'
    assert result.stderr == ""


def test_wrapper_normalizes_nested_json_output() -> None:
    result = _run_script(
        """python -c "print('{\\\"position\\\": {\\\"x\\\": 3.0, \\\"y\\\": 9.25}}')" """
    )

    assert result.returncode == 0
    assert result.stdout.strip() == '{"x": 3.0, "y": 9.25}'
    assert result.stderr == ""


def test_wrapper_normalizes_csv_output() -> None:
    result = _run_script("""python -c "print('12.5,-4.0')" """)

    assert result.returncode == 0
    assert result.stdout.strip() == '{"x": 12.5, "y": -4.0}'
    assert result.stderr == ""


def test_wrapper_fails_when_raw_command_is_missing() -> None:
    result = _run_script(None)

    assert result.returncode == 1
    assert "FACTORIO_RAW_POSITION_COMMAND is not set" in result.stderr


def test_wrapper_fails_when_raw_command_returns_error() -> None:
    result = _run_script(
        """python -c "import sys; print('boom', file=sys.stderr); sys.exit(1)" """
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "boom" in result.stderr