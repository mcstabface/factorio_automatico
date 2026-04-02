from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from artifacts.run_artifact_writer import RunArtifactWriter
from contracts.actions import Action
from contracts.artifacts import ActionExecutionResult, RunAudit
from executors.factorio_move_executor import FactorioMoveExecutor
from executors.stub_action_executor import StubActionExecutor
from experts.action_validation_expert import ActionValidationExpert
from experts.state_normalization_expert import StateNormalizationExpert
from integrations.factorio.factorio_client import FactorioClient


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "mock_world_state.json"
DEFAULT_ARTIFACT_ROOT = Path(__file__).resolve().parents[1] / "runs"
RUN_ID = "single_action_mock_run"


def _load_mock_world_state() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_move_to_action() -> Action:
    return Action.move_to(
        action_id="move-to-bootstrap-position",
        x=5.0,
        y=3.0,
        preconditions=("world state is normalized",),
        expected_effects=("player target position is echoed by executor",),
    )


def _build_executor(
    executor_type: Literal["stub", "factorio"],
) -> StubActionExecutor | FactorioMoveExecutor:
    if executor_type == "stub":
        return StubActionExecutor()

    if executor_type == "factorio":
        return FactorioMoveExecutor(FactorioClient())

    raise ValueError(f"Unsupported executor_type: {executor_type}")


def run_single_action(
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    executor_type: Literal["stub", "factorio"] = "stub",
    run_id: str = RUN_ID,
    raw_state: dict[str, Any] | None = None,
    candidate_action: Action | dict[str, Any] | None = None,
) -> dict[str, Any]:
    if raw_state is None:
        raw_state = _load_mock_world_state()

    if candidate_action is None:
        candidate_action = _build_move_to_action()

    normalization_expert = StateNormalizationExpert()
    normalization_result = normalization_expert.run(raw_state, run_id)

    action_validation_expert = ActionValidationExpert()
    action_validation_result = action_validation_expert.run(
        candidate_action,
        normalization_result.world_state,
        run_id,
    )

    executor = _build_executor(executor_type)
    execution_result: ActionExecutionResult = executor.execute(
        action_validation_result.action
    )

    run_audit = RunAudit(
        run_id=run_id,
        pipeline=(
            "state_normalization",
            "action_validation",
            f"{executor_type}_execution",
            "artifact_write",
        ),
        executor_type=executor_type,
        status="success",
    )

    writer = RunArtifactWriter(artifact_root)
    run_dir = writer.write_run_artifacts(
        run_id=run_id,
        input_state_snapshot=raw_state,
        state_normalization_debug=normalization_result.debug_artifact,
        validated_action=action_validation_result.action,
        action_validation_debug=action_validation_result.debug_artifact,
        execution_result=execution_result,
        run_audit=run_audit,
    )

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "executor_type": executor_type,
        "validated_action": asdict(action_validation_result.action),
        "execution_result": asdict(execution_result),
        "run_audit": asdict(run_audit),
    }