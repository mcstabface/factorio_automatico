from __future__ import annotations

import json
from pathlib import Path

import pytest

from contracts.actions import Action
from director.run_single_action import RUN_ID, run_seed_replay_demo, run_single_action


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
        "post_execution_observation.json",
        "movement_transition.json",
        "terminal_trace.json",
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
    post_execution_observation = json.loads(
        (run_dir / "post_execution_observation.json").read_text(encoding="utf-8")
    )
    movement_transition = json.loads(
        (run_dir / "movement_transition.json").read_text(encoding="utf-8")
    )
    terminal_trace = json.loads(
        (run_dir / "terminal_trace.json").read_text(encoding="utf-8")
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
    assert post_execution_observation["observation_type"] == "stub"
    assert post_execution_observation["status"] == "not_available"
    assert (
        post_execution_observation["reason"]
        == "stub executor does not provide live game observation"
    )
    assert result["post_execution_observation"] == post_execution_observation
    assert movement_transition["before_position"] == {"x": 0.0, "y": 0.0}
    assert movement_transition["requested_target_position"] == {"x": 5.0, "y": 3.0}
    assert movement_transition["after_position"] == post_execution_observation
    assert result["movement_transition"] == movement_transition
    assert terminal_trace["title"] == "Factorio MES Single Action Trace"
    assert terminal_trace["mode"] == "stub"
    assert (
    terminal_trace["summary"]
    == "MOVE_TO accepted via stub_action_executor from seed demo-seed-001"
)
    assert terminal_trace["events"][0]["step"] == "state_normalization"
    assert terminal_trace["events"][1]["step"] == "action_validation"
    assert terminal_trace["events"][2]["step"] == "stub_execution"
    assert terminal_trace["events"][3]["step"] == "post_execution_observation"
    assert terminal_trace["events"][4]["step"] == "movement_transition"
    assert terminal_trace["events"][0]["status"] == "success"
    assert terminal_trace["events"][0]["payload"]["seed"] == "demo-seed-001"
    assert terminal_trace["events"][0]["payload"]["starting_position"] == {
        "x": 0.0,
        "y": 0.0,
    }
    assert terminal_trace["events"][0]["payload"]["tick"] == 123
    assert terminal_trace["events"][1]["status"] == "success"
    assert terminal_trace["events"][2]["status"] == "accepted"
    assert terminal_trace["events"][3]["status"] == "success"
    assert terminal_trace["events"][4]["status"] == "success"
    assert result["terminal_trace"] == terminal_trace
    assert run_audit["run_id"] == RUN_ID
    assert run_audit["executor_type"] == "stub"
    assert run_audit["pipeline"][2] == "stub_execution"
    assert run_audit["pipeline"][3] == "post_execution_observation"


def test_run_single_action_pipeline_with_factorio_executor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FACTORIO_POSITION_COMMAND", raising=False)
    monkeypatch.delenv("FACTORIO_MOVE_TO_COMMAND", raising=False)
    result = run_single_action(tmp_path, executor_type="factorio")

    run_dir = tmp_path / RUN_ID
    execution_result = json.loads(
        (run_dir / "execution_result.json").read_text(encoding="utf-8")
    )
    post_execution_observation = json.loads(
        (run_dir / "post_execution_observation.json").read_text(encoding="utf-8")
    )
    movement_transition = json.loads(
        (run_dir / "movement_transition.json").read_text(encoding="utf-8")
    )
    terminal_trace = json.loads(
        (run_dir / "terminal_trace.json").read_text(encoding="utf-8")
    )
    run_audit = json.loads((run_dir / "run_audit.json").read_text(encoding="utf-8"))

    assert result["executor_type"] == "factorio"
    assert execution_result["success"] is True
    assert execution_result["executor_name"] == "factorio_move_executor"
    assert execution_result["action_type"] == "MOVE_TO"
    assert execution_result["execution_status"] == "accepted"
    assert execution_result["target_position"] == {"x": 5.0, "y": 3.0}
    assert execution_result["observed_result"]["movement_started"] is True
    assert execution_result["observed_result"]["movement_completed"] is True
    assert execution_result["error_message"] is None
    assert result["post_execution_observation"] == post_execution_observation
    assert post_execution_observation == {"x": 5.0, "y": 3.0}
    assert movement_transition["before_position"] == {"x": 0.0, "y": 0.0}
    assert movement_transition["requested_target_position"] == {"x": 5.0, "y": 3.0}
    assert movement_transition["after_position"] == {"x": 5.0, "y": 3.0}
    assert result["movement_transition"] == movement_transition
    assert terminal_trace["title"] == "Factorio MES Single Action Trace"
    assert terminal_trace["mode"] == "factorio"
    assert (
    terminal_trace["summary"]
    == "MOVE_TO accepted via factorio_move_executor from seed demo-seed-001"
)
    assert terminal_trace["events"][0]["step"] == "state_normalization"
    assert terminal_trace["events"][1]["step"] == "action_validation"
    assert terminal_trace["events"][2]["step"] == "factorio_execution"
    assert terminal_trace["events"][3]["step"] == "post_execution_observation"
    assert terminal_trace["events"][4]["step"] == "movement_transition"
    assert terminal_trace["events"][0]["status"] == "success"
    assert terminal_trace["events"][0]["payload"]["seed"] == "demo-seed-001"
    assert terminal_trace["events"][0]["payload"]["starting_position"] == {
        "x": 0.0,
        "y": 0.0,
    }
    assert terminal_trace["events"][0]["payload"]["tick"] == 123
    assert terminal_trace["events"][2]["status"] == "accepted"
    assert terminal_trace["events"][2]["payload"]["movement_started"] is True
    assert terminal_trace["events"][2]["payload"]["movement_completed"] is True
    assert result["terminal_trace"] == terminal_trace
    assert run_audit["run_id"] == RUN_ID
    assert run_audit["executor_type"] == "factorio"
    assert run_audit["pipeline"][2] == "factorio_execution"
    assert run_audit["pipeline"][3] == "post_execution_observation"


def test_run_single_action_pipeline_with_factorio_executor_seed_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FACTORIO_POSITION_COMMAND", raising=False)
    monkeypatch.delenv("FACTORIO_MOVE_TO_COMMAND", raising=False)
    result = run_single_action(
        tmp_path,
        executor_type="factorio",
        factorio_seed="viewer-seed-777",
    )

    run_dir = tmp_path / RUN_ID
    terminal_trace = json.loads(
        (run_dir / "terminal_trace.json").read_text(encoding="utf-8")
    )
    input_state_snapshot = json.loads(
        (run_dir / "input_state_snapshot.json").read_text(encoding="utf-8")
    )

    assert result["executor_type"] == "factorio"
    assert input_state_snapshot["world_session"]["seed"] == "viewer-seed-777"
    assert terminal_trace["mode"] == "factorio"
    assert (
        terminal_trace["summary"]
        == "MOVE_TO accepted via factorio_move_executor from seed viewer-seed-777"
    )
    assert terminal_trace["events"][0]["payload"]["seed"] == "viewer-seed-777"
    assert terminal_trace["events"][0]["payload"]["starting_position"] == {
        "x": 0.0,
        "y": 0.0,
    }
    assert result["terminal_trace"] == terminal_trace


def test_run_seed_replay_demo_returns_matching_factorio_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FACTORIO_POSITION_COMMAND", raising=False)
    monkeypatch.delenv("FACTORIO_MOVE_TO_COMMAND", raising=False)
    result = run_seed_replay_demo(
        artifact_root=tmp_path,
        factorio_seed="viewer-seed-777",
        emit_terminal_trace=False,
    )

    assert result["seed"] == "viewer-seed-777"
    assert result["matching_summary"] is True
    assert result["matching_trace_events"] is True
    assert result["matching_movement_transition"] is True

    first_run = result["first_run"]
    second_run = result["second_run"]

    assert first_run["executor_type"] == "factorio"
    assert second_run["executor_type"] == "factorio"

    assert (
        first_run["terminal_trace"]["summary"]
        == "MOVE_TO accepted via factorio_move_executor from seed viewer-seed-777"
    )
    assert (
        second_run["terminal_trace"]["summary"]
        == "MOVE_TO accepted via factorio_move_executor from seed viewer-seed-777"
    )

    assert first_run["terminal_trace"]["events"] == second_run["terminal_trace"]["events"]
    assert first_run["movement_transition"] == second_run["movement_transition"]
    assert first_run["terminal_trace"]["events"][0]["payload"]["seed"] == "viewer-seed-777"
    assert second_run["terminal_trace"]["events"][0]["payload"]["seed"] == "viewer-seed-777"


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
    movement_transition = json.loads(
        (run_dir / "movement_transition.json").read_text(encoding="utf-8")
    )

    assert result["run_id"] == custom_run_id
    assert input_state_snapshot["tick"] == 456
    assert input_state_snapshot["player"]["position"] == {"x": 10.0, "y": 20.0}
    assert state_normalization_debug["tick"] == 456
    assert movement_transition["before_position"] == {"x": 10.0, "y": 20.0}


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
    movement_transition = json.loads(
        (run_dir / "movement_transition.json").read_text(encoding="utf-8")
    )

    assert result["run_id"] == custom_run_id
    assert validated_action["action_id"] == "move-to-custom-position"
    assert validated_action["params"]["target_position"] == {"x": 9.0, "y": 7.0}
    assert execution_result["target_position"] == {"x": 9.0, "y": 7.0}
    assert movement_transition["requested_target_position"] == {"x": 9.0, "y": 7.0}