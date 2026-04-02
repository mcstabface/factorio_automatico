from __future__ import annotations

from typing import Any

from contracts.actions import Action, ActionType
from contracts.artifacts import ActionExecutionResult, MovementObservation
from contracts.world_state import Position


class FactorioMoveExecutor:
    executor_name = "factorio_move_executor"

    def __init__(self, factorio_client: Any) -> None:
        self.factorio_client = factorio_client

    def execute(self, action: Action) -> ActionExecutionResult:
        if action.action_type is not ActionType.MOVE_TO:
            raise ValueError(
                f"FactorioMoveExecutor supports only {ActionType.MOVE_TO.value}"
            )

        target_position = action.params.get("target_position")
        if not isinstance(target_position, dict):
            raise ValueError("MOVE_TO requires params.target_position")

        normalized_target_position = Position(
            x=float(target_position["x"]),
            y=float(target_position["y"]),
        )

        adapter_result = self.factorio_client.move_to(
            normalized_target_position.x,
            normalized_target_position.y,
        )

        movement_started = adapter_result.started
        movement_completed = adapter_result.completed

        return ActionExecutionResult(
            success=movement_started,
            executor_name=self.executor_name,
            action_id=action.action_id,
            action_type=action.action_type,
            execution_status="accepted" if movement_started else "rejected",
            target_position=normalized_target_position,
            observed_result=MovementObservation(
                movement_started=movement_started,
                movement_completed=movement_completed,
            ),
            error_message=None if movement_started else "move_to was not accepted",
        )

    def observe_player_position(self) -> Position:
        return self.factorio_client.get_player_position()