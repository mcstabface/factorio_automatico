from __future__ import annotations

from dataclasses import dataclass
import json
import os
import subprocess
from typing import Any

from contracts.world_state import Position

MOVE_TO_COMPLETION_TOLERANCE = 0.75

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
        position_probe_command: str | None = None,
        position_probe_timeout_seconds: float = 2.0,
        move_to_command: str | None = None,
        move_to_timeout_seconds: float = 5.0,
    ) -> None:
        self._seed = seed
        self._starting_position = starting_position or Position(x=0.0, y=0.0)
        self._player_position = self._starting_position
        self._position_probe_command = (
            position_probe_command or os.environ.get("FACTORIO_POSITION_COMMAND")
        )
        self._position_probe_timeout_seconds = position_probe_timeout_seconds
        self._move_to_command = move_to_command or os.environ.get("FACTORIO_MOVE_TO_COMMAND")
        self._move_to_timeout_seconds = move_to_timeout_seconds

    def get_seed(self) -> str:
        return self._seed

    def get_starting_position(self) -> Position:
        return self._starting_position

    def reset_to_seed(self, seed: str | None = None) -> None:
        if seed is not None:
            self._seed = seed
        self._player_position = self._starting_position

    def _read_live_player_position(self) -> Position | None:
        if not self._position_probe_command:
            return None

        try:
            completed_process = subprocess.run(
                self._position_probe_command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._position_probe_timeout_seconds,
            )
        except (OSError, subprocess.SubprocessError):
            return None

        if completed_process.returncode != 0:
            return None

        probe_output = completed_process.stdout.strip()
        if not probe_output:
            return None

        return self._parse_position_probe_output(probe_output)

    def _parse_position_probe_output(self, probe_output: str) -> Position | None:
        last_line = probe_output.splitlines()[-1].strip()
        if not last_line:
            return None

        parsed_output: Any | None = None
        try:
            parsed_output = json.loads(last_line)
        except json.JSONDecodeError:
            parsed_output = None

        if isinstance(parsed_output, dict):
            direct_position = self._position_from_mapping(parsed_output)
            if direct_position is not None:
                return direct_position

            nested_position = parsed_output.get("position")
            if isinstance(nested_position, dict):
                return self._position_from_mapping(nested_position)

        if "," not in last_line:
            return None

        x_str, y_str = [part.strip() for part in last_line.split(",", maxsplit=1)]
        try:
            return Position(x=float(x_str), y=float(y_str))
        except ValueError:
            return None

    @staticmethod
    def _position_from_mapping(payload: dict[str, Any]) -> Position | None:
        if "x" not in payload or "y" not in payload:
            return None

        try:
            return Position(
                x=float(payload["x"]),
                y=float(payload["y"]),
            )
        except (TypeError, ValueError):
            return None

    def _execute_live_move_to(self, x: float, y: float) -> Position | None:
        if not self._move_to_command:
            return None

        command = f"{self._move_to_command} {float(x)} {float(y)}"

        try:
            completed_process = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._move_to_timeout_seconds,
            )
        except (OSError, subprocess.SubprocessError):
            return None

        if completed_process.returncode != 0:
            return None

        move_output = completed_process.stdout.strip()
        if not move_output:
            return None

        return self._parse_position_probe_output(move_output)

    def get_player_position(self) -> Position:
        live_position = self._read_live_player_position()
        if live_position is not None:
            self._player_position = live_position
        return self._player_position

    def get_world_state_snapshot(self) -> dict[str, object]:
        live_position = self.get_player_position()

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
                    "x": live_position.x,
                    "y": live_position.y,
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

    @staticmethod
    def _is_within_completion_tolerance(
        observed_position: Position,
        target_position: Position,
    ) -> bool:
        dx = target_position.x - observed_position.x
        dy = target_position.y - observed_position.y
        return (dx * dx + dy * dy) ** 0.5 <= MOVE_TO_COMPLETION_TOLERANCE

    def move_to(self, x: float, y: float) -> MoveToCommandResult:
        target_position = Position(
            x=float(x),
            y=float(y),
        )

        last_known_position = self._player_position

        live_position = self._execute_live_move_to(x=target_position.x, y=target_position.y)
        if live_position is not None:
            self._player_position = live_position
            completed = self._is_within_completion_tolerance(
                observed_position=self._player_position,
                target_position=target_position,
            )
        else:
            self._player_position = last_known_position
            completed = False

        return MoveToCommandResult(
            started=True,
            completed=completed,
            command="move_to",
            target_position=target_position,
        )