from __future__ import annotations

import subprocess

import pytest

from scripts import run_live_demo_sequence as sequence_script


def test_main_runs_smoke_then_stream_demo_and_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[str] = []

    def _fake_run_command(command: str) -> subprocess.CompletedProcess[str]:
        calls.append(command)

        if command == "python scripts/smoke_live_bridge.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout='{"delta": {"x": 1.0, "y": 0.0}}',
                stderr="",
            )

        if command == "python scripts/run_live_factorio_stream_demo.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout='{"result_status": "target_reached", "steps_taken": 2}',
                stderr="stream demo trace",
            )

        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(sequence_script, "_run_command", _fake_run_command)

    result = sequence_script.main()
    captured = capsys.readouterr()

    assert result == 0
    assert calls == [
        "python scripts/smoke_live_bridge.py",
        "python scripts/run_live_factorio_stream_demo.py",
    ]

    assert captured.out.strip() == '{"result_status": "target_reached", "steps_taken": 2}'

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "sequence: starting live smoke check",
        '{"delta": {"x": 1.0, "y": 0.0}}',
        "sequence: smoke check passed",
        "sequence: starting stream demo",
        "stream demo trace",
        "sequence: stream demo completed successfully",
    ]


def test_main_stops_when_smoke_check_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[str] = []

    def _fake_run_command(command: str) -> subprocess.CompletedProcess[str]:
        calls.append(command)

        if command == "python scripts/smoke_live_bridge.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=1,
                stdout="",
                stderr="smoke failed",
            )

        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(sequence_script, "_run_command", _fake_run_command)

    result = sequence_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert calls == ["python scripts/smoke_live_bridge.py"]
    assert captured.out == ""

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "sequence: starting live smoke check",
        "smoke failed",
        "sequence: stopped because smoke check failed",
    ]


def test_main_returns_one_when_stream_demo_command_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[str] = []

    def _fake_run_command(command: str) -> subprocess.CompletedProcess[str]:
        calls.append(command)

        if command == "python scripts/smoke_live_bridge.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )

        if command == "python scripts/run_live_factorio_stream_demo.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=2,
                stdout="",
                stderr="boom",
            )

        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(sequence_script, "_run_command", _fake_run_command)

    result = sequence_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert calls == [
        "python scripts/smoke_live_bridge.py",
        "python scripts/run_live_factorio_stream_demo.py",
    ]
    assert captured.out == ""

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "sequence: starting live smoke check",
        "sequence: smoke check passed",
        "sequence: starting stream demo",
        "boom",
        "sequence: stream demo command error",
    ]


def test_main_preserves_bounded_failure_return_code_from_stream_demo(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[str] = []

    def _fake_run_command(command: str) -> subprocess.CompletedProcess[str]:
        calls.append(command)

        if command == "python scripts/smoke_live_bridge.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )

        if command == "python scripts/run_live_factorio_stream_demo.py":
            return subprocess.CompletedProcess(
                args=command,
                returncode=1,
                stdout='{"result_status": "max_steps_reached", "steps_taken": 12}',
                stderr="bounded failure trace",
            )

        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(sequence_script, "_run_command", _fake_run_command)

    result = sequence_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert calls == [
        "python scripts/smoke_live_bridge.py",
        "python scripts/run_live_factorio_stream_demo.py",
    ]
    assert captured.out.strip() == '{"result_status": "max_steps_reached", "steps_taken": 12}'

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "sequence: starting live smoke check",
        "sequence: smoke check passed",
        "sequence: starting stream demo",
        "bounded failure trace",
        "sequence: stream demo completed with bounded failure",
    ]