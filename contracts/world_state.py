from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a mapping")
    return value


def _require_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _require_number(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be a number")
    return float(value)


def _require_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return value


@dataclass(frozen=True, slots=True)
class Position:
    x: float
    y: float

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str) -> "Position":
        mapping = _require_mapping(data, field_name)
        return cls(
            x=_require_number(mapping.get("x"), f"{field_name}.x"),
            y=_require_number(mapping.get("y"), f"{field_name}.y"),
        )


@dataclass(frozen=True, slots=True)
class WorldSessionState:
    seed: str | None
    starting_position: Position | None

    @classmethod
    def from_mapping(
        cls, data: Any, *, field_name: str = "world_session"
    ) -> "WorldSessionState":
        if data is None:
            return cls(seed=None, starting_position=None)

        mapping = _require_mapping(data, field_name)
        seed = mapping.get("seed")
        starting_position = mapping.get("starting_position")

        if seed is not None:
            seed = _require_str(seed, f"{field_name}.seed")

        if starting_position is not None:
            starting_position = Position.from_mapping(
                starting_position,
                field_name=f"{field_name}.starting_position",
            )

        return cls(
            seed=seed,
            starting_position=starting_position,
        )


@dataclass(frozen=True, slots=True)
class InventoryItem:
    name: str
    count: int

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str) -> "InventoryItem":
        mapping = _require_mapping(data, field_name)
        count = _require_int(mapping.get("count"), f"{field_name}.count")
        if count < 0:
            raise ValueError(f"{field_name}.count must be >= 0")
        return cls(
            name=_require_str(mapping.get("name"), f"{field_name}.name"),
            count=count,
        )


@dataclass(frozen=True, slots=True)
class CraftingQueueItem:
    recipe_name: str
    count: int

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str) -> "CraftingQueueItem":
        mapping = _require_mapping(data, field_name)
        count = _require_int(mapping.get("count"), f"{field_name}.count")
        if count < 0:
            raise ValueError(f"{field_name}.count must be >= 0")
        return cls(
            recipe_name=_require_str(
                mapping.get("recipe_name"), f"{field_name}.recipe_name"
            ),
            count=count,
        )


@dataclass(frozen=True, slots=True)
class PlayerState:
    position: Position
    reach_distance: float
    mining_speed: float
    inventory: tuple[InventoryItem, ...]
    crafting_queue: tuple[CraftingQueueItem, ...]

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str = "player") -> "PlayerState":
        mapping = _require_mapping(data, field_name)
        reach_distance = _require_number(
            mapping.get("reach_distance"), f"{field_name}.reach_distance"
        )
        mining_speed = _require_number(
            mapping.get("mining_speed"), f"{field_name}.mining_speed"
        )
        if reach_distance < 0:
            raise ValueError(f"{field_name}.reach_distance must be >= 0")
        if mining_speed < 0:
            raise ValueError(f"{field_name}.mining_speed must be >= 0")

        inventory_data = mapping.get("inventory")
        if not isinstance(inventory_data, list):
            raise TypeError(f"{field_name}.inventory must be a list")

        queue_data = mapping.get("crafting_queue")
        if not isinstance(queue_data, list):
            raise TypeError(f"{field_name}.crafting_queue must be a list")

        return cls(
            position=Position.from_mapping(
                mapping.get("position"), field_name=f"{field_name}.position"
            ),
            reach_distance=reach_distance,
            mining_speed=mining_speed,
            inventory=tuple(
                InventoryItem.from_mapping(
                    item, field_name=f"{field_name}.inventory[{i}]"
                )
                for i, item in enumerate(inventory_data)
            ),
            crafting_queue=tuple(
                CraftingQueueItem.from_mapping(
                    item, field_name=f"{field_name}.crafting_queue[{i}]"
                )
                for i, item in enumerate(queue_data)
            ),
        )


@dataclass(frozen=True, slots=True)
class NearbyResource:
    resource_name: str
    position: Position
    amount: int

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str) -> "NearbyResource":
        mapping = _require_mapping(data, field_name)
        amount = _require_int(mapping.get("amount"), f"{field_name}.amount")
        if amount < 0:
            raise ValueError(f"{field_name}.amount must be >= 0")
        return cls(
            resource_name=_require_str(
                mapping.get("resource_name"), f"{field_name}.resource_name"
            ),
            position=Position.from_mapping(
                mapping.get("position"), field_name=f"{field_name}.position"
            ),
            amount=amount,
        )


@dataclass(frozen=True, slots=True)
class NearbyEntity:
    entity_id: str
    entity_name: str
    entity_type: str
    position: Position

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str) -> "NearbyEntity":
        mapping = _require_mapping(data, field_name)
        return cls(
            entity_id=_require_str(
                mapping.get("entity_id"), f"{field_name}.entity_id"
            ),
            entity_name=_require_str(
                mapping.get("entity_name"), f"{field_name}.entity_name"
            ),
            entity_type=_require_str(
                mapping.get("entity_type"), f"{field_name}.entity_type"
            ),
            position=Position.from_mapping(
                mapping.get("position"), field_name=f"{field_name}.position"
            ),
        )


@dataclass(frozen=True, slots=True)
class RecipeAvailability:
    craftable_now: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Any, *, field_name: str = "recipes"
    ) -> "RecipeAvailability":
        mapping = _require_mapping(data, field_name)
        craftable_now = mapping.get("craftable_now")
        if not isinstance(craftable_now, list):
            raise TypeError(f"{field_name}.craftable_now must be a list")
        return cls(
            craftable_now=tuple(
                _require_str(value, f"{field_name}.craftable_now[{i}]")
                for i, value in enumerate(craftable_now)
            )
        )


@dataclass(frozen=True, slots=True)
class Buildability:
    placeable_entities: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Any, *, field_name: str = "buildability"
    ) -> "Buildability":
        mapping = _require_mapping(data, field_name)
        placeable_entities = mapping.get("placeable_entities")
        if not isinstance(placeable_entities, list):
            raise TypeError(f"{field_name}.placeable_entities must be a list")
        return cls(
            placeable_entities=tuple(
                _require_str(value, f"{field_name}.placeable_entities[{i}]")
                for i, value in enumerate(placeable_entities)
            )
        )


@dataclass(frozen=True, slots=True)
class Objective:
    current_goal: str | None

    @classmethod
    def from_mapping(cls, data: Any, *, field_name: str = "objective") -> "Objective":
        if data is None:
            return cls(current_goal=None)

        mapping = _require_mapping(data, field_name)
        current_goal = mapping.get("current_goal")

        if current_goal is None:
            return cls(current_goal=None)

        return cls(current_goal=_require_str(current_goal, f"{field_name}.current_goal"))


@dataclass(frozen=True, slots=True)
class WorldState:
    tick: int
    world_session: WorldSessionState
    player: PlayerState
    nearby_resources: tuple[NearbyResource, ...]
    nearby_entities: tuple[NearbyEntity, ...]
    recipes: RecipeAvailability
    buildability: Buildability
    objective: Objective

    @classmethod
    def from_mapping(cls, data: Any) -> "WorldState":
        mapping = _require_mapping(data, "world_state")
        tick = _require_int(mapping.get("tick"), "world_state.tick")
        if tick < 0:
            raise ValueError("world_state.tick must be >= 0")

        resources_data = mapping.get("nearby_resources")
        if not isinstance(resources_data, list):
            raise TypeError("world_state.nearby_resources must be a list")

        entities_data = mapping.get("nearby_entities")
        if not isinstance(entities_data, list):
            raise TypeError("world_state.nearby_entities must be a list")

        return cls(
            tick=tick,
            world_session=WorldSessionState.from_mapping(
                mapping.get("world_session")
            ),
            player=PlayerState.from_mapping(mapping.get("player")),
            nearby_resources=tuple(
                NearbyResource.from_mapping(
                    item, field_name=f"world_state.nearby_resources[{i}]"
                )
                for i, item in enumerate(resources_data)
            ),
            nearby_entities=tuple(
                NearbyEntity.from_mapping(
                    item, field_name=f"world_state.nearby_entities[{i}]"
                )
                for i, item in enumerate(entities_data)
            ),
            recipes=RecipeAvailability.from_mapping(mapping.get("recipes")),
            buildability=Buildability.from_mapping(mapping.get("buildability")),
            objective=Objective.from_mapping(mapping.get("objective")),
        )