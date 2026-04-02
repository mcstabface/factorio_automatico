from __future__ import annotations

import json
from pathlib import Path

from director.run_single_action import RUN_ID, run_single_action


def test_run_single_action_pipeline(tmp_path: Path) -> None:
    result = run_single_action(tmp_path)

    run_dir = tmp_path / RUN_ID
    assert result["run_id"] == RUN_ID
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

    assert validated_action["action_type"] == "MOVE_TO"
    assert state_normalization_debug["success"] is True
    assert state_normalization_debug["warnings"] == []
    assert state_normalization_debug["error_message"] is None
    assert state_normalization_debug["duration_ms"] == 0
    assert state_normalization_debug["input_ref"] is None
    assert state_normalization_debug["output_ref"] is None
    assert action_validation_debug["success"] is True
    assert action_validation_debug["warnings"] == []
    assert action_validation_debug["error_message"] is None
    assert action_validation_debug["duration_ms"] == 0
    assert action_validation_debug["input_ref"] is None
    assert action_validation_debug["output_ref"] is None
    assert execution_result["success"] is True
    assert execution_result["executor_name"] == "stub_action_executor"
    assert execution_result["action_type"] == "MOVE_TO"
    assert execution_result["execution_status"] == "accepted"
    assert execution_result["target_position"] == {"x": 5.0, "y": 3.0}
    assert execution_result["observed_result"]["movement_started"] is True
    assert execution_result["observed_result"]["movement_completed"] is False
    assert execution_result["error_message"] is None
