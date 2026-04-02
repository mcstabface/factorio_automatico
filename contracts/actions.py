from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a mapping")
    return value


def _require_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{name} must be a non-empty string")
    return value


class ActionType(str, Enum):
    MOVE_TO = "MOVE_TO"
    MINE_RESOURCE = "MINE_RESOURCE"
    CRAFT_RECIPE = "CRAFT_RECIPE"
    PLACE_ENTITY = "PLACE_ENTITY"
    INTERACT_ENTITY = "INTERACT_ENTITY"
    NO_OP = "NO_OP"


@dataclass(frozen=True, slots=True)
class Action:
    action_id: str
    action_type: ActionType
    params: dict[str, Any]
    preconditions: tuple[str, ...]
    expected_effects: tuple[str, ...]

    @classmethod
    def move_to(
        cls,
        *,
        action_id: str,
        x: float,
        y: float,
        preconditions: tuple[str, ...] = (),
        expected_effects: tuple[str, ...] = (),
    ) -> "Action":
        return cls(
            action_id=action_id,
            action_type=ActionType.MOVE_TO,
            params={
                "target_position": {
                    "x": float(x),
                    "y": float(y),
                }
            },
            preconditions=preconditions,
            expected_effects=expected_effects,
        )

    @classmethod
    def from_mapping(cls, data: Any) -> "Action":
        mapping = _require_mapping(data, "action")
        params = mapping.get("params")
        if not isinstance(params, dict):
            raise TypeError("action.params must be a mapping")

        preconditions = mapping.get("preconditions")
        if not isinstance(preconditions, list):
            raise TypeError("action.preconditions must be a list")

        expected_effects = mapping.get("expected_effects")
        if not isinstance(expected_effects, list):
            raise TypeError("action.expected_effects must be a list")

        action_type_value = _require_str(mapping.get("action_type"), "action.action_type")

        return cls(
            action_id=_require_str(mapping.get("action_id"), "action.action_id"),
            action_type=ActionType(action_type_value),
            params=dict(params),
            preconditions=tuple(
                _require_str(value, f"action.preconditions[{i}]")
                for i, value in enumerate(preconditions)
            ),
            expected_effects=tuple(
                _require_str(value, f"action.expected_effects[{i}]")
                for i, value in enumerate(expected_effects)
            ),
        )