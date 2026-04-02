from __future__ import annotations

from typing import Any

from contracts.actions import Action, ActionType
from contracts.world_state import Position, WorldState
from validation.state_validator import validate_world_state


def _inventory_count(world_state: WorldState, item_name: str) -> int:
    for item in world_state.player.inventory:
        if item.name == item_name:
            return item.count
    return 0


def _require_param_str(action: Action, key: str) -> str:
    value = action.params.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{action.action_type.value} requires params.{key}")
    return value


def _require_param_position(action: Action, key: str) -> Position:
    value = action.params.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{action.action_type.value} requires params.{key}")
    return Position.from_mapping(value, field_name=f"action.params.{key}")


def validate_action(
    action: Action | dict[str, Any], world_state: WorldState | dict[str, Any]
) -> Action:
    normalized_world_state = validate_world_state(world_state)
    normalized_action = action if isinstance(action, Action) else Action.from_mapping(action)

    if normalized_action.action_type is ActionType.MOVE_TO:
        _require_param_position(normalized_action, "target_position")
        return normalized_action

    if normalized_action.action_type is ActionType.PLACE_ENTITY:
        entity_name = _require_param_str(normalized_action, "entity_name")
        if entity_name not in normalized_world_state.buildability.placeable_entities:
            raise ValueError(f"{entity_name} is not placeable in the current world state")
        if _inventory_count(normalized_world_state, entity_name) <= 0:
            raise ValueError(f"inventory count for {entity_name} must be greater than zero")
        return normalized_action

    if normalized_action.action_type is ActionType.CRAFT_RECIPE:
        recipe_name = _require_param_str(normalized_action, "recipe_name")
        if recipe_name not in normalized_world_state.recipes.craftable_now:
            raise ValueError(f"{recipe_name} is not craftable_now")
        return normalized_action

    if normalized_action.action_type is ActionType.MINE_RESOURCE:
        resource_name = _require_param_str(normalized_action, "resource_name")
        target_position = _require_param_position(normalized_action, "target_position")
        if all(
            resource.resource_name != resource_name
            or resource.position != target_position
            for resource in normalized_world_state.nearby_resources
        ):
            raise ValueError(
                f"{resource_name} is not present at target_position in nearby_resources"
            )
        return normalized_action

    if normalized_action.action_type is ActionType.INTERACT_ENTITY:
        target_entity_id = _require_param_str(normalized_action, "target_entity_id")
        if all(
            entity.entity_id != target_entity_id
            for entity in normalized_world_state.nearby_entities
        ):
            raise ValueError(f"{target_entity_id} is not present in nearby_entities")
        return normalized_action

    if normalized_action.action_type is ActionType.NO_OP:
        return normalized_action

    raise ValueError(f"Unsupported action type: {normalized_action.action_type}")