from __future__ import annotations

from typing import Any

from contracts.actions import Action, ActionType


class FactorioMoveExecutor:
    def __init__(self, factorio_client: Any) -> None:
        self.factorio_client = factorio_client

    def execute(self, action: Action) -> dict[str, object]:
        if action.action_type is not ActionType.MOVE_TO:
            raise ValueError(
                f"FactorioMoveExecutor supports only {ActionType.MOVE_TO.value}"
            )

        target_position = action.params.get("target_position")
        if not isinstance(target_position, dict):
            raise ValueError("MOVE_TO requires params.target_position")

        x = float(target_position["x"])
        y = float(target_position["y"])
        adapter_result = self.factorio_client.move_to(x, y)

        return {
            "success": True,
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "target_position": {"x": x, "y": y},
            "adapter_result": adapter_result,
        }
