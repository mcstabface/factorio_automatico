from __future__ import annotations

import subprocess

import pytest

from contracts.world_state import Position
from integrations.factorio.factorio_client import FactorioClient


def test_live_probe_updates_player_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='{"x": 7.5, "y": -2.0}\n',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    client = FactorioClient(position_probe_command="fake-position-probe")

    assert client.get_player_position() == Position(x=7.5, y=-2.0)


def test_failed_live_probe_falls_back_to_cached_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="boom",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    client = FactorioClient(
        position_probe_command="fake-position-probe",
        starting_position=Position(x=1.0, y=2.0),
    )

    assert client.get_player_position() == Position(x=1.0, y=2.0)
    assert client.get_world_state_snapshot()["player"]["position"] == {
        "x": 1.0,
        "y": 2.0,
    }

def test_live_move_command_updates_cached_player_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        command = args[0]
        if command == "fake-move-command 5.0 3.0":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout='{"x": 5.0, "y": 3.0}\n',
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="unexpected command",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    client = FactorioClient(move_to_command="fake-move-command")

    result = client.move_to(5.0, 3.0)

    assert result.started is True
    assert result.completed is False
    assert result.target_position == Position(x=5.0, y=3.0)
    assert client.get_player_position() == Position(x=5.0, y=3.0)


def test_failed_live_move_command_falls_back_to_target_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="boom",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    client = FactorioClient(move_to_command="fake-move-command")

    result = client.move_to(8.0, -1.5)

    assert result.started is True
    assert result.completed is False
    assert result.target_position == Position(x=8.0, y=-1.5)
    assert client.get_player_position() == Position(x=8.0, y=-1.5)