from __future__ import annotations

import json
import subprocess

import pytest

from scripts import run_live_factorio_stream_demo as stream_demo_script


def _parse_summary(captured_stdout: str) -> dict[str, object]:
    return json.loads(captured_stdout)


def test_main_emits_stream_header_footer_and_json_summary_for_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    summary = {
        "demo_type": "bounded_multi_step_walk",
        "starting_position": {"x": 2.0, "y": 3.0},
        "requested_offset": {"x": 5.0, "y": 5.0},
        "requested_target": {"x": 7.0, "y": 8.0},
        "result_status": "target_reached",
        "steps_taken": 2,
        "final_position": {"x": 6.8, "y": 7.9},
        "walk_summary": {
            "status": "target_reached",
            "steps_taken": 2,
            "final_position": {"x": 6.8, "y": 7.9},
        },
    }

    def _fake_run_demo_command() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/run_live_factorio_demo.py",
            returncode=0,
            stdout=json.dumps(summary),
            stderr="walk start: demo trace\nwalk stop: target reached in 2 step(s)\n",
        )

    monkeypatch.setattr(stream_demo_script, "_run_demo_command", _fake_run_demo_command)

    result = stream_demo_script.main()
    captured = capsys.readouterr()

    assert result == 0
    assert _parse_summary(captured.out) == summary

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "walk start: demo trace",
        "walk stop: target reached in 2 step(s)",
        "=== Factorio Live Demo ===",
        "start=(2.000, 3.000) offset=(5.000, 5.000) target=(7.000, 8.000)",
        "result=target_reached steps=2 final=(6.800, 7.900)",
        "=== End Factorio Live Demo ===",
    ]


def test_main_preserves_return_code_one_for_bounded_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    summary = {
        "demo_type": "bounded_multi_step_walk",
        "starting_position": {"x": 10.0, "y": 10.0},
        "requested_offset": {"x": 5.0, "y": 5.0},
        "requested_target": {"x": 15.0, "y": 15.0},
        "result_status": "max_steps_reached",
        "steps_taken": 12,
        "final_position": {"x": 12.0, "y": 12.0},
        "walk_summary": {
            "status": "max_steps_reached",
            "steps_taken": 12,
            "final_position": {"x": 12.0, "y": 12.0},
        },
    }

    def _fake_run_demo_command() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/run_live_factorio_demo.py",
            returncode=1,
            stdout=json.dumps(summary),
            stderr="walk start: demo trace\nwalk stop: max steps reached (12)\n",
        )

    monkeypatch.setattr(stream_demo_script, "_run_demo_command", _fake_run_demo_command)

    result = stream_demo_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert _parse_summary(captured.out) == summary

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "walk start: demo trace",
        "walk stop: max steps reached (12)",
        "=== Factorio Live Demo ===",
        "start=(10.000, 10.000) offset=(5.000, 5.000) target=(15.000, 15.000)",
        "result=max_steps_reached steps=12 final=(12.000, 12.000)",
        "=== End Factorio Live Demo ===",
    ]


def test_main_returns_one_when_underlying_demo_output_is_not_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _fake_run_demo_command() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/run_live_factorio_demo.py",
            returncode=0,
            stdout="definitely not json",
            stderr="walk start: demo trace\n",
        )

    monkeypatch.setattr(stream_demo_script, "_run_demo_command", _fake_run_demo_command)

    result = stream_demo_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "walk start: demo trace",
        "stream demo failed: underlying demo output was not valid JSON",
    ]


def test_main_returns_one_when_underlying_demo_command_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def _fake_run_demo_command() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args="python scripts/run_live_factorio_demo.py",
            returncode=2,
            stdout="",
            stderr="boom",
        )

    monkeypatch.setattr(stream_demo_script, "_run_demo_command", _fake_run_demo_command)

    result = stream_demo_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "boom",
        "stream demo failed: underlying demo command error",
    ]