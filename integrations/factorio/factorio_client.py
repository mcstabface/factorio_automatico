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
    def get_player_position(self) -> Position:
        return Position(x=0.0, y=0.0)

    def move_to(self, x: float, y: float) -> MoveToCommandResult:
        return MoveToCommandResult(
            started=True,
            completed=False,
            command="move_to",
            target_position=Position(
                x=float(x),
                y=float(y),
            ),
        )