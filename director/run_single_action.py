from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from artifacts.run_artifact_writer import RunArtifactWriter
from contracts.actions import Action, ActionType
from contracts.artifacts import ActionExecutionResult
from executors.stub_action_executor import StubActionExecutor
from experts.action_validation_expert import ActionValidationExpert
from experts.state_normalization_expert import StateNormalizationExpert


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "mock_world_state.json"
DEFAULT_ARTIFACT_ROOT = Path(__file__).resolve().parents[1] / "runs"
RUN_ID = "single_action_mock_run"


def _load_mock_world_state() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_move_to_action() -> Action:
    return Action(
        action_id="move-to-bootstrap-position",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 5.0, "y": 3.0}},
        preconditions=("world state is normalized",),
        expected_effects=("player target position is echoed by stub executor",),
    )


def run_single_action(artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT) -> dict[str, Any]:
    raw_state = _load_mock_world_state()

    normalization_expert = StateNormalizationExpert()
    normalization_result = normalization_expert.run(raw_state, RUN_ID)

    candidate_action = _build_move_to_action()
    action_validation_expert = ActionValidationExpert()
    action_validation_result = action_validation_expert.run(
        candidate_action,
        normalization_result.world_state,
        RUN_ID,
    )

    executor = StubActionExecutor()
    execution_result: ActionExecutionResult = executor.execute(
        action_validation_result.action
    )

    run_audit = {
        "run_id": RUN_ID,
        "pipeline": [
            "state_normalization",
            "action_validation",
            "stub_execution",
            "artifact_write",
        ],
        "status": "success",
    }

    writer = RunArtifactWriter(artifact_root)
    run_dir = writer.write_run_artifacts(
        run_id=RUN_ID,
        input_state_snapshot=raw_state,
        state_normalization_debug=normalization_result.debug_artifact,
        validated_action=action_validation_result.action,
        action_validation_debug=action_validation_result.debug_artifact,
        execution_result=asdict(execution_result),
        run_audit=run_audit,
    )

    return {
        "run_id": RUN_ID,
        "run_dir": str(run_dir),
        "validated_action": asdict(action_validation_result.action),
        "execution_result": asdict(execution_result),
        "run_audit": run_audit,
    }
