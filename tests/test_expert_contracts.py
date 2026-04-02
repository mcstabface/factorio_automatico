from __future__ import annotations

from contracts.actions import Action, ActionType
from contracts.world_state import WorldState
from experts.action_validation_expert import ActionValidationExpert
from experts.state_normalization_expert import StateNormalizationExpert


def _valid_world_state() -> dict:
    return {
        "tick": 123,
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
    }


def _valid_move_to_action() -> Action:
    return Action(
        action_id="move-1",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 5.0, "y": 3.0}},
        preconditions=("world state is normalized",),
        expected_effects=("player target position is echoed by executor",),
    )


def test_state_normalization_expert_accepts_dict_input() -> None:
    expert = StateNormalizationExpert()

    result = expert.run(_valid_world_state(), run_id="run-001")

    assert result.world_state.tick == 123
    assert result.debug_artifact.run_id == "run-001"
    assert result.debug_artifact.tick == 123
    assert result.debug_artifact.summary == "State normalized and validated."


def test_state_normalization_expert_accepts_world_state_input() -> None:
    expert = StateNormalizationExpert()
    world_state = WorldState.from_mapping(_valid_world_state())

    result = expert.run(world_state, run_id="run-002")

    assert result.world_state is world_state
    assert result.debug_artifact.run_id == "run-002"
    assert result.debug_artifact.tick == 123
    assert result.debug_artifact.summary == "State normalized and validated."


def test_action_validation_expert_accepts_dict_world_state_input() -> None:
    expert = ActionValidationExpert()
    action = _valid_move_to_action()

    result = expert.run(action, _valid_world_state(), run_id="run-003")

    assert result.action.action_id == "move-1"
    assert result.debug_artifact.run_id == "run-003"
    assert result.debug_artifact.tick == 123
    assert "objective=NONE" in result.debug_artifact.considered_facts


def test_action_validation_expert_accepts_world_state_input() -> None:
    expert = ActionValidationExpert()
    action = _valid_move_to_action()
    world_state = WorldState.from_mapping(_valid_world_state())

    result = expert.run(action, world_state, run_id="run-004")

    assert result.action.action_id == "move-1"
    assert result.debug_artifact.run_id == "run-004"
    assert result.debug_artifact.tick == 123
    assert "objective=NONE" in result.debug_artifact.considered_facts