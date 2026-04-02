from __future__ import annotations

import json
from pathlib import Path

import pytest

from contracts.actions import Action
from director.run_single_action import RUN_ID, run_single_action


def _custom_raw_state() -> dict:
    return {
        "tick": 456,
        "player": {
            "position": {"x": 10.0, "y": 20.0},
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


def _custom_move_action() -> Action:
    return Action.move_to(
        action_id="move-to-custom-position",
        x=9.0,
        y=7.0,
        preconditions=("world state is normalized",),
        expected_effects=("player target position is echoed by executor",),
    )


def test_run_single_action_pipeline_with_stub_executor(tmp_path: Path) -> None:
    result = run_single_action(tmp_path, executor_type="stub")

    run_dir = tmp_path / RUN_ID
    assert result["run_id"] == RUN_ID
    assert result["executor_type"] == "stub"
    assert run_dir.exists()

    expected_files = (
        "input_state_snapshot.json",
        "state_normalization_debug.json",
        "validated_action.json",
        "action_validation_debug.json",
        "execution_result.json",
        "run_audit.json",
    )
    for filename in expected_files:
        assert (run_dir / filename).exists()

    validated_action = json.loads(
        (run_dir / "validated_action.json").read_text(encoding="utf-8")
    )
    state_normalization_debug = json.loads(
        (run_dir / "state_normalization_debug.json").read_text(encoding="utf-8")
    )
    action_validation_debug = json.loads(
        (run_dir / "action_validation_debug.json").read_text(encoding="utf-8")
    )
    execution_result = json.loads(
        (run_dir / "execution_result.json").read_text(encoding="utf-8")
    )
    run_audit = json.loads((run_dir / "run_audit.json").read_text(encoding="utf-8"))

    assert validated_action["action_type"] == "MOVE_TO"
    assert state_normalization_debug["run_id"] == RUN_ID
    assert state_normalization_debug["success"] is True
    assert state_normalization_debug["warnings"] == []
    assert state_normalization_debug["error_message"] is None
    assert state_normalization_debug["duration_ms"] == 0
    assert state_normalization_debug["input_ref"] is None
    assert state_normalization_debug["output_ref"] is None
    assert state_normalization_debug["proposed_actions"] == []
    assert action_validation_debug["run_id"] == RUN_ID
    assert action_validation_debug["success"] is True
    assert action_validation_debug["warnings"] == []
    assert action_validation_debug["error_message"] is None
    assert action_validation_debug["duration_ms"] == 0
    assert action_validation_debug["input_ref"] is None
    assert action_validation_debug["output_ref"] is None
    assert len(action_validation_debug["proposed_actions"]) == 1
    assert execution_result["success"] is True
    assert execution_result["executor_name"] == "stub_action_executor"
    assert execution_result["action_type"] == "MOVE_TO"
    assert execution_result["execution_status"] == "accepted"
    assert execution_result["target_position"] == {"x": 5.0, "y": 3.0}
    assert execution_result["observed_result"]["movement_started"] is True
    assert execution_result["observed_result"]["movement_completed"] is False
    assert execution_result["error_message"] is None
    assert run_audit["run_id"] == RUN_ID
    assert run_audit["executor_type"] == "stub"
    assert run_audit["pipeline"][2] == "stub_execution"


def test_run_single_action_pipeline_with_factorio_executor(tmp_path: Path) -> None:
    result = run_single_action(tmp_path, executor_type="factorio")

    run_dir = tmp_path / RUN_ID
    execution_result = json.loads(
        (run_dir / "execution_result.json").read_text(encoding="utf-8")
    )
    run_audit = json.loads((run_dir / "run_audit.json").read_text(encoding="utf-8"))

    assert result["executor_type"] == "factorio"
    assert execution_result["success"] is True
    assert execution_result["executor_name"] == "factorio_move_executor"
    assert execution_result["action_type"] == "MOVE_TO"
    assert execution_result["execution_status"] == "accepted"
    assert execution_result["target_position"] == {"x": 5.0, "y": 3.0}
    assert execution_result["observed_result"]["movement_started"] is True
    assert execution_result["observed_result"]["movement_completed"] is False
    assert execution_result["error_message"] is None
    assert run_audit["run_id"] == RUN_ID
    assert run_audit["executor_type"] == "factorio"
    assert run_audit["pipeline"][2] == "factorio_execution"


def test_run_single_action_rejects_unsupported_executor_type(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported executor_type: invalid"):
        run_single_action(tmp_path, executor_type="invalid")


def test_run_single_action_accepts_custom_run_id(tmp_path: Path) -> None:
    custom_run_id = "custom-run-001"

    result = run_single_action(
        tmp_path,
        executor_type="stub",
        run_id=custom_run_id,
    )

    run_dir = tmp_path / custom_run_id
    state_normalization_debug = json.loads(
        (run_dir / "state_normalization_debug.json").read_text(encoding="utf-8")
    )
    action_validation_debug = json.loads(
        (run_dir / "action_validation_debug.json").read_text(encoding="utf-8")
    )
    run_audit = json.loads((run_dir / "run_audit.json").read_text(encoding="utf-8"))

    assert result["run_id"] == custom_run_id
    assert run_dir.exists()
    assert state_normalization_debug["run_id"] == custom_run_id
    assert action_validation_debug["run_id"] == custom_run_id
    assert run_audit["run_id"] == custom_run_id


def test_run_single_action_accepts_explicit_raw_state(tmp_path: Path) -> None:
    custom_run_id = "custom-raw-state-run"
    raw_state = _custom_raw_state()

    result = run_single_action(
        tmp_path,
        executor_type="stub",
        run_id=custom_run_id,
        raw_state=raw_state,
    )

    run_dir = tmp_path / custom_run_id
    input_state_snapshot = json.loads(
        (run_dir / "input_state_snapshot.json").read_text(encoding="utf-8")
    )
    state_normalization_debug = json.loads(
        (run_dir / "state_normalization_debug.json").read_text(encoding="utf-8")
    )

    assert result["run_id"] == custom_run_id
    assert input_state_snapshot["tick"] == 456
    assert input_state_snapshot["player"]["position"] == {"x": 10.0, "y": 20.0}
    assert state_normalization_debug["tick"] == 456


def test_run_single_action_accepts_explicit_candidate_action(tmp_path: Path) -> None:
    custom_run_id = "custom-action-run"
    candidate_action = _custom_move_action()

    result = run_single_action(
        tmp_path,
        executor_type="stub",
        run_id=custom_run_id,
        candidate_action=candidate_action,
    )

    run_dir = tmp_path / custom_run_id
    validated_action = json.loads(
        (run_dir / "validated_action.json").read_text(encoding="utf-8")
    )
    execution_result = json.loads(
        (run_dir / "execution_result.json").read_text(encoding="utf-8")
    )

    assert result["run_id"] == custom_run_id
    assert validated_action["action_id"] == "move-to-custom-position"
    assert validated_action["params"]["target_position"] == {"x": 9.0, "y": 7.0}
    assert execution_result["target_position"] == {"x": 9.0, "y": 7.0}