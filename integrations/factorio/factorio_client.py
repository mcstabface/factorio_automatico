from __future__ import annotations

from dataclasses import dataclass

from contracts.world_state import Position


@dataclass(frozen=True, slots=True)
class MoveToCommandResult:
    started: bool
    completed: bool
    command: str
    target_position: Position


class FactorioClient:
    def __init__(self) -> None:
        self._player_position = Position(x=0.0, y=0.0)

    def get_player_position(self) -> Position:
        return self._player_position

    def move_to(self, x: float, y: float) -> MoveToCommandResult:
        target_position = Position(
            x=float(x),
            y=float(y),
        )
        self._player_position = target_position

        return MoveToCommandResult(
            started=True,
            completed=False,
            command="move_to",
            target_position=target_position,
        )