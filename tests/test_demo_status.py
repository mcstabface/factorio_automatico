from __future__ import annotations

import json
import subprocess

import pytest

from scripts import demo_status


def _parse_summary(captured_stdout: str) -> dict[str, object]:
    return json.loads(captured_stdout)


def test_main_returns_zero_and_recommends_demo_commands_when_ready(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    env_summary = {
        "overall_ok": True,
        "repo_root": "/tmp/factorio_automatico",
        "checks": {
            "rcon_listener": {
                "ok": True,
                "details": "accepting connections",
                "value": "127.0.0.1:27015",
            }
        },
    }

    def _fake_run_env_check() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/check_factorio_bridge_env.py",
            returncode=0,
            stdout=json.dumps(env_summary),
            stderr="",
        )

    monkeypatch.setattr(demo_status, "_run_env_check", _fake_run_env_check)

    result = demo_status.main()
    captured = capsys.readouterr()

    assert result == 0

    summary = _parse_summary(captured.out)
    assert summary == {
        "overall_ok": True,
        "recommended_next_commands": [
            "python scripts/smoke_live_bridge.py",
            "python scripts/run_live_factorio_stream_demo.py",
            "python scripts/run_live_factorio_walk_to_target.py --trace 10 10",
        ],
        "repo_root": "/tmp/factorio_automatico",
    }

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "demo status: live bridge looks ready",
        "next: python scripts/smoke_live_bridge.py",
        "next: python scripts/run_live_factorio_stream_demo.py",
        "next: python scripts/run_live_factorio_walk_to_target.py --trace 10 10",
    ]


def test_main_returns_one_and_recommends_startup_commands_when_not_ready(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    env_summary = {
        "overall_ok": False,
        "repo_root": "/tmp/factorio_automatico",
        "checks": {
            "rcon_listener": {
                "ok": False,
                "details": "not accepting connections",
                "value": "127.0.0.1:27015",
            }
        },
    }

    def _fake_run_env_check() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/check_factorio_bridge_env.py",
            returncode=1,
            stdout=json.dumps(env_summary),
            stderr="",
        )

    monkeypatch.setattr(demo_status, "_run_env_check", _fake_run_env_check)

    result = demo_status.main()
    captured = capsys.readouterr()

    assert result == 1

    summary = _parse_summary(captured.out)
    assert summary == {
        "overall_ok": False,
        "recommended_next_commands": [
            "bash scripts/start_factorio_headless.sh",
            "source scripts/set_factorio_bridge_env.sh",
            "python scripts/check_factorio_bridge_env.py",
        ],
        "repo_root": "/tmp/factorio_automatico",
    }

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "demo status: live bridge not ready yet",
        "next: bash scripts/start_factorio_headless.sh",
        "next: source scripts/set_factorio_bridge_env.sh",
        "next: python scripts/check_factorio_bridge_env.py",
    ]


def test_main_returns_one_when_env_check_output_is_not_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _fake_run_env_check() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/check_factorio_bridge_env.py",
            returncode=0,
            stdout="not json",
            stderr="",
        )

    monkeypatch.setattr(demo_status, "_run_env_check", _fake_run_env_check)

    result = demo_status.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err.strip() == "demo status failed: env check output was not valid JSON"


def test_main_returns_one_when_env_check_command_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _fake_run_env_check() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/check_factorio_bridge_env.py",
            returncode=2,
            stdout="",
            stderr="boom",
        )

    monkeypatch.setattr(demo_status, "_run_env_check", _fake_run_env_check)

    result = demo_status.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "boom",
        "demo status failed: env check command error",
    ]


def test_recommended_commands_falls_back_when_checks_shape_is_invalid() -> None:
    summary = {
        "overall_ok": False,
        "checks": "definitely not a mapping",
    }

    assert demo_status._recommended_commands(summary) == [
        "python scripts/check_factorio_bridge_env.py"
    ]