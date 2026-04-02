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