import pytest

from contracts.world_state import WorldState
from validation.action_validator import validate_action
from validation.state_validator import validate_world_state


def _valid_world_state() -> dict:
    return {
        "tick": 123,
        "world_session": {
            "seed": "demo-seed-001",
            "starting_position": {"x": 0.0, "y": 0.0},
        },
        "player": {
            "position": {"x": 0.0, "y": 0.0},
            "reach_distance": 10.0,
            "mining_speed": 0.5,
            "inventory": [
                {"name": "burner-mining-drill", "count": 1},
                {"name": "iron-plate", "count": 3},
            ],
            "crafting_queue": [{"recipe_name": "iron-gear-wheel", "count": 1}],
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
        "recipes": {"craftable_now": ["iron-gear-wheel"]},
        "buildability": {"placeable_entities": ["burner-mining-drill"]},
        "objective": {"current_goal": "bootstrap iron production"},
    }


def test_valid_world_state() -> None:
    validated = validate_world_state(_valid_world_state())
    assert validated.tick == 123
    assert validated.world_session.seed == "demo-seed-001"
    assert validated.world_session.starting_position is not None
    assert validated.world_session.starting_position.x == 0.0
    assert validated.world_session.starting_position.y == 0.0
    assert validated.objective.current_goal == "bootstrap iron production"


def test_validate_world_state_returns_same_instance_for_world_state_input() -> None:
    world_state = WorldState.from_mapping(_valid_world_state())

    validated = validate_world_state(world_state)

    assert validated is world_state


def test_valid_world_state_with_missing_world_session_block() -> None:
    world_state = _valid_world_state()
    del world_state["world_session"]

    validated = validate_world_state(world_state)
    assert validated.world_session.seed is None
    assert validated.world_session.starting_position is None


def test_valid_world_state_with_null_objective() -> None:
    world_state = _valid_world_state()
    world_state["objective"]["current_goal"] = None

    validated = validate_world_state(world_state)
    assert validated.objective.current_goal is None


def test_valid_world_state_with_missing_objective_block() -> None:
    world_state = _valid_world_state()
    del world_state["objective"]

    validated = validate_world_state(world_state)
    assert validated.objective.current_goal is None


def test_invalid_world_state_with_empty_objective_string() -> None:
    world_state = _valid_world_state()
    world_state["objective"]["current_goal"] = ""

    with pytest.raises((TypeError, ValueError)):
        validate_world_state(world_state)


def test_invalid_world_state_with_empty_seed_string() -> None:
    world_state = _valid_world_state()
    world_state["world_session"]["seed"] = ""

    with pytest.raises((TypeError, ValueError)):
        validate_world_state(world_state)


def test_invalid_world_state_with_malformed_starting_position() -> None:
    world_state = _valid_world_state()
    world_state["world_session"]["starting_position"] = {"x": 0.0}

    with pytest.raises((TypeError, ValueError)):
        validate_world_state(world_state)


def test_invalid_world_state_missing_required_fields() -> None:
    invalid_state = _valid_world_state()
    del invalid_state["player"]["position"]

    with pytest.raises((TypeError, ValueError)):
        validate_world_state(invalid_state)


def test_valid_move_to_action() -> None:
    action = {
        "action_id": "move-1",
        "action_type": "MOVE_TO",
        "params": {"target_position": {"x": 10.0, "y": 5.0}},
        "preconditions": [],
        "expected_effects": ["player is closer to target"],
    }

    validated = validate_action(action, _valid_world_state())
    assert validated.action_id == "move-1"


def test_invalid_move_to_action_missing_target_position() -> None:
    action = {
        "action_id": "move-2",
        "action_type": "MOVE_TO",
        "params": {},
        "preconditions": [],
        "expected_effects": ["player is closer to target"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_move_to_action_malformed_target_position() -> None:
    action = {
        "action_id": "move-3",
        "action_type": "MOVE_TO",
        "params": {"target_position": {"x": 10.0}},
        "preconditions": [],
        "expected_effects": ["player is closer to target"],
    }

    with pytest.raises((TypeError, ValueError)):
        validate_action(action, _valid_world_state())


def test_invalid_place_entity_action_missing_entity_name() -> None:
    action = {
        "action_id": "place-2",
        "action_type": "PLACE_ENTITY",
        "params": {},
        "preconditions": ["entity is placeable"],
        "expected_effects": ["entity exists in world"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_craft_recipe_action_missing_recipe_name() -> None:
    action = {
        "action_id": "craft-2",
        "action_type": "CRAFT_RECIPE",
        "params": {},
        "preconditions": [],
        "expected_effects": ["item added to inventory"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_mine_resource_action_missing_resource_name() -> None:
    action = {
        "action_id": "mine-1",
        "action_type": "MINE_RESOURCE",
        "params": {"target_position": {"x": 2.0, "y": 1.0}},
        "preconditions": [],
        "expected_effects": ["resource added to inventory"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_mine_resource_action_missing_target_position() -> None:
    action = {
        "action_id": "mine-2",
        "action_type": "MINE_RESOURCE",
        "params": {"resource_name": "iron-ore"},
        "preconditions": [],
        "expected_effects": ["resource added to inventory"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_mine_resource_action_target_position_mismatch() -> None:
    action = {
        "action_id": "mine-3",
        "action_type": "MINE_RESOURCE",
        "params": {
            "resource_name": "iron-ore",
            "target_position": {"x": 99.0, "y": 99.0},
        },
        "preconditions": [],
        "expected_effects": ["resource added to inventory"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_interact_entity_action_missing_target_entity_id() -> None:
    action = {
        "action_id": "interact-1",
        "action_type": "INTERACT_ENTITY",
        "params": {},
        "preconditions": [],
        "expected_effects": ["entity interaction occurs"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_interact_entity_action_unknown_target_entity_id() -> None:
    action = {
        "action_id": "interact-2",
        "action_type": "INTERACT_ENTITY",
        "params": {"target_entity_id": "entity-999"},
        "preconditions": [],
        "expected_effects": ["entity interaction occurs"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())


def test_invalid_place_entity_action_when_inventory_missing_or_zero() -> None:
    world_state = _valid_world_state()
    world_state["player"]["inventory"] = [{"name": "burner-mining-drill", "count": 0}]
    action = {
        "action_id": "place-1",
        "action_type": "PLACE_ENTITY",
        "params": {"entity_name": "burner-mining-drill"},
        "preconditions": ["entity is placeable"],
        "expected_effects": ["entity exists in world"],
    }

    with pytest.raises(ValueError):
        validate_action(action, world_state)


def test_invalid_craft_recipe_action_when_recipe_not_craftable_now() -> None:
    action = {
        "action_id": "craft-1",
        "action_type": "CRAFT_RECIPE",
        "params": {"recipe_name": "transport-belt"},
        "preconditions": [],
        "expected_effects": ["transport-belt added to inventory"],
    }

    with pytest.raises(ValueError):
        validate_action(action, _valid_world_state())