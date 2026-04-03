from __future__ import annotations

import json

import pytest

from contracts.world_state import Position
from integrations.factorio.factorio_client import MoveToCommandResult
from scripts import run_live_factorio_walk_to_target as walk_script


class FakeFactorioClient:
    def __init__(
        self,
        positions: list[Position],
    ) -> None:
        if not positions:
            raise ValueError("positions must not be empty")
        self._positions = positions
        self._read_index = 0
        self.move_calls: list[tuple[float, float]] = []

    def get_player_position(self) -> Position:
        if self._read_index >= len(self._positions):
            return self._positions[-1]

        position = self._positions[self._read_index]
        self._read_index += 1
        return position

    def move_to(self, x: float, y: float) -> MoveToCommandResult:
        self.move_calls.append((x, y))
        return MoveToCommandResult(
            started=True,
            completed=False,
            command="move_to",
            target_position=Position(x=float(x), y=float(y)),
        )


def _parse_summary(captured_stdout: str) -> dict[str, object]:
    return json.loads(captured_stdout)


def test_main_returns_already_within_tolerance_without_move(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(
        positions=[
            Position(x=10.1015625, y=10.1015625),
        ]
    )

    monkeypatch.setattr(walk_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(
        walk_script,
        "sys",
        type(
            "FakeSys",
            (),
            {"argv": ["run_live_factorio_walk_to_target.py", "10", "10"]},
        ),
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 0

    summary = _parse_summary(captured.out)
    assert summary["status"] == "already_within_tolerance"
    assert summary["steps_taken"] == 0
    assert summary["step_history"] == []
    assert fake_client.move_calls == []


def test_main_returns_target_reached_after_progress(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(
        positions=[
            Position(x=0.0, y=0.0),
            Position(x=4.8, y=4.8),
        ]
    )

    monkeypatch.setattr(walk_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(
        walk_script,
        "sys",
        type(
            "FakeSys",
            (),
            {
                "argv": [
                    "run_live_factorio_walk_to_target.py",
                    "5",
                    "5",
                    "0.5",
                    "4",
                    "0.05",
                ]
            },
        ),
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 0

    summary = _parse_summary(captured.out)
    assert summary["status"] == "target_reached"
    assert summary["steps_taken"] == 1
    assert len(summary["step_history"]) == 1
    assert fake_client.move_calls == [(5.0, 5.0)]


def test_main_returns_stuck_no_progress_when_progress_is_too_small(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(
        positions=[
            Position(x=0.0, y=0.0),
            Position(x=0.01, y=0.01),
        ]
    )

    monkeypatch.setattr(walk_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(
        walk_script,
        "sys",
        type(
            "FakeSys",
            (),
            {
                "argv": [
                    "run_live_factorio_walk_to_target.py",
                    "5",
                    "5",
                    "0.5",
                    "4",
                    "0.05",
                ]
            },
        ),
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1

    summary = _parse_summary(captured.out)
    assert summary["status"] == "stuck_no_progress"
    assert summary["steps_taken"] == 1
    assert len(summary["step_history"]) == 1
    assert fake_client.move_calls == [(5.0, 5.0)]


def test_main_returns_max_steps_reached_when_progress_continues_but_target_is_not_reached(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_client = FakeFactorioClient(
        positions=[
            Position(x=0.0, y=0.0),
            Position(x=1.0, y=1.0),
            Position(x=2.0, y=2.0),
        ]
    )

    monkeypatch.setattr(walk_script, "FactorioClient", lambda: fake_client)
    monkeypatch.setattr(
        walk_script,
        "sys",
        type(
            "FakeSys",
            (),
            {
                "argv": [
                    "run_live_factorio_walk_to_target.py",
                    "5",
                    "5",
                    "0.5",
                    "2",
                    "0.05",
                ]
            },
        ),
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1

    summary = _parse_summary(captured.out)
    assert summary["status"] == "max_steps_reached"
    assert summary["steps_taken"] == 2
    assert len(summary["step_history"]) == 2
    assert fake_client.move_calls == [(5.0, 5.0), (5.0, 5.0)]


def test_main_returns_error_for_invalid_numeric_args(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        walk_script.sys,
        "argv",
        [
            "run_live_factorio_walk_to_target.py",
            "five",
            "5",
        ],
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert (
        captured.err.strip()
        == "x, y, tolerance, max_steps, and min_progress must be numeric"
    )


def test_main_returns_error_for_non_positive_max_steps(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        walk_script.sys,
        "argv",
        [
            "run_live_factorio_walk_to_target.py",
            "5",
            "5",
            "0.5",
            "0",
            "0.05",
        ],
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err.strip() == "max_steps must be > 0"


def test_main_returns_error_for_wrong_arg_count(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        walk_script.sys,
        "argv",
        [
            "run_live_factorio_walk_to_target.py",
            "5",
        ],
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert (
        captured.err.strip()
        == "usage: python scripts/run_live_factorio_walk_to_target.py <x> <y> [tolerance] [max_steps] [min_progress]"
    )


def test_main_returns_error_for_negative_tolerance(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        walk_script.sys,
        "argv",
        [
            "run_live_factorio_walk_to_target.py",
            "5",
            "5",
            "-0.1",
        ],
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err.strip() == "tolerance must be >= 0"


def test_main_returns_error_for_negative_min_progress(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        walk_script.sys,
        "argv",
        [
            "run_live_factorio_walk_to_target.py",
            "5",
            "5",
            "0.5",
            "4",
            "-0.01",
        ],
    )

    result = walk_script.main()
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err.strip() == "min_progress must be >= 0"