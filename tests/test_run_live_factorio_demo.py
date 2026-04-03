from __future__ import annotations

import json

import pytest

from contracts.world_state import Position
from scripts import run_live_factorio_demo as demo_script


class FakeFactorioClient:
    def __init__(self, position: Position) -> None:
        self._position = position

    def get_player_position(self) -> Position:
        return self._position


def _parse_summary(captured_stdout: str) -> dict[str, object]:
    return json.loads(captured_stdout)


def test_main_returns_zero_and_emits_stream_friendly_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(Position(x=2.0, y=3.0))

    def _fake_run_walk_to_target(
        *,
        client: FakeFactorioClient,
        target_position: Position,
        tolerance: float,
        max_steps: int,
        min_progress: float,
        trace_sink,
    ) -> dict[str, object]:
        assert client is fake_client
        assert target_position == Position(x=7.0, y=8.0)

        trace_sink("walk start: demo trace")
        trace_sink("walk stop: target reached in 2 step(s)")

        return {
            "status": "target_reached",
            "target_position": {"x": 7.0, "y": 8.0},
            "tolerance": tolerance,
            "max_steps": max_steps,
            "min_progress": min_progress,
            "initial_position": {"x": 2.0, "y": 3.0},
            "final_position": {"x": 6.8, "y": 7.9},
            "initial_distance": 7.0710678118654755,
            "final_distance": 0.22360679774997896,
            "steps_taken": 2,
            "step_history": [],
        }

    monkeypatch.setattr(demo_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(demo_script, "run_walk_to_target", _fake_run_walk_to_target)

    result = demo_script.main()
    captured = capsys.readouterr()

    assert result == 0

    summary = _parse_summary(captured.out)
    assert summary == {
        "demo_type": "bounded_multi_step_walk",
        "starting_position": {"x": 2.0, "y": 3.0},
        "requested_offset": {"x": 5.0, "y": 5.0},
        "requested_target": {"x": 7.0, "y": 8.0},
        "result_status": "target_reached",
        "steps_taken": 2,
        "final_position": {"x": 6.8, "y": 7.9},
        "walk_summary": {
            "status": "target_reached",
            "target_position": {"x": 7.0, "y": 8.0},
            "tolerance": demo_script.DEFAULT_TOLERANCE,
            "max_steps": demo_script.DEFAULT_MAX_STEPS,
            "min_progress": demo_script.DEFAULT_MIN_PROGRESS,
            "initial_position": {"x": 2.0, "y": 3.0},
            "final_position": {"x": 6.8, "y": 7.9},
            "initial_distance": 7.0710678118654755,
            "final_distance": 0.22360679774997896,
            "steps_taken": 2,
            "step_history": [],
        },
    }

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "walk start: demo trace",
        "walk stop: target reached in 2 step(s)",
    ]


def test_main_returns_one_when_walk_does_not_reach_target(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(Position(x=10.0, y=10.0))

    def _fake_run_walk_to_target(
        *,
        client: FakeFactorioClient,
        target_position: Position,
        tolerance: float,
        max_steps: int,
        min_progress: float,
        trace_sink,
    ) -> dict[str, object]:
        assert client is fake_client
        assert target_position == Position(x=15.0, y=15.0)

        trace_sink("walk start: demo trace")
        trace_sink("walk stop: max steps reached (12)")

        return {
            "status": "max_steps_reached",
            "target_position": {"x": 15.0, "y": 15.0},
            "tolerance": tolerance,
            "max_steps": max_steps,
            "min_progress": min_progress,
            "initial_position": {"x": 10.0, "y": 10.0},
            "final_position": {"x": 12.0, "y": 12.0},
            "initial_distance": 7.0710678118654755,
            "final_distance": 4.242640687119285,
            "steps_taken": 12,
            "step_history": [],
        }

    monkeypatch.setattr(demo_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(demo_script, "run_walk_to_target", _fake_run_walk_to_target)

    result = demo_script.main()
    captured = capsys.readouterr()

    assert result == 1

    summary = _parse_summary(captured.out)
    assert summary["result_status"] == "max_steps_reached"
    assert summary["steps_taken"] == 12
    assert summary["starting_position"] == {"x": 10.0, "y": 10.0}
    assert summary["requested_target"] == {"x": 15.0, "y": 15.0}
    assert summary["final_position"] == {"x": 12.0, "y": 12.0}

    trace_lines = [line.strip() for line in captured.err.splitlines() if line.strip()]
    assert trace_lines == [
        "walk start: demo trace",
        "walk stop: max steps reached (12)",
    ]