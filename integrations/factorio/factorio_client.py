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
    def __init__(
        self,
        *,
        seed: str = "demo-seed-001",
        starting_position: Position | None = None,
    ) -> None:
        self._seed = seed
        self._starting_position = starting_position or Position(x=0.0, y=0.0)
        self._player_position = self._starting_position

    def get_seed(self) -> str:
        return self._seed

    def get_starting_position(self) -> Position:
        return self._starting_position

    def reset_to_seed(self, seed: str | None = None) -> None:
        if seed is not None:
            self._seed = seed
        self._player_position = self._starting_position

    def get_player_position(self) -> Position:
        return self._player_position

    def get_world_state_snapshot(self) -> dict[str, object]:
        return {
            "tick": 123,
            "world_session": {
                "seed": self._seed,
                "starting_position": {
                    "x": self._starting_position.x,
                    "y": self._starting_position.y,
                },
            },
            "player": {
                "position": {
                    "x": self._player_position.x,
                    "y": self._player_position.y,
                },
                "reach_distance": 10.0,
                "mining_speed": 0.5,
                "inventory": [
                    {"name": "burner-mining-drill", "count": 1},
                    {"name": "iron-plate", "count": 3},
                ],
                "crafting_queue": [
                    {"recipe_name": "iron-gear-wheel", "count": 1}
                ],
            },
            "nearby_resources": [
                {
                    "resource_name": "iron-ore",
                    "position": {"x": 2.0, "y": 1.0},
                    "amount": 500,
                }
            ],
            "nearby_entities": [
                {
                    "entity_id": "entity-001",
                    "entity_name": "stone-furnace",
                    "entity_type": "furnace",
                    "position": {"x": 1.0, "y": 1.0},
                }
            ],
            "recipes": {
                "craftable_now": ["iron-gear-wheel"]
            },
            "buildability": {
                "placeable_entities": ["burner-mining-drill"]
            },
            "objective": {
                "current_goal": "bootstrap iron production"
            },
        }

    def restart_from_seed(self, seed: str | None = None) -> dict[str, object]:
        self.reset_to_seed(seed)
        return self.get_world_state_snapshot()

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