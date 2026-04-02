from __future__ import annotations

from typing import Any

from contracts.world_state import WorldState


def validate_world_state(world_state: WorldState | dict[str, Any]) -> WorldState:
    if isinstance(world_state, WorldState):
        normalized = world_state
    else:
        normalized = WorldState.from_mapping(world_state)

    if normalized.tick < 0:
        raise ValueError("world_state.tick must be >= 0")

    return normalized
