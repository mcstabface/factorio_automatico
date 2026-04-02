from __future__ import annotations

from contracts.actions import Action, ActionType
from contracts.artifacts import ActionExecutionResult, MovementObservation
from contracts.world_state import Position


class StubActionExecutor:
    executor_name = "stub_action_executor"

    def execute(self, action: Action) -> ActionExecutionResult:
        if action.action_type is not ActionType.MOVE_TO:
            raise ValueError(
                f"StubActionExecutor supports only {ActionType.MOVE_TO.value}"
            )

        target_position = action.params["target_position"]
        normalized_target_position = Position(
            x=float(target_position["x"]),
            y=float(target_position["y"]),
        )

        return ActionExecutionResult(
            success=True,
            executor_name=self.executor_name,
            action_id=action.action_id,
            action_type=action.action_type,
            execution_status="accepted",
            target_position=normalized_target_position,
            observed_result=MovementObservation(
                movement_started=True,
                movement_completed=False,
            ),
            error_message=None,
        )