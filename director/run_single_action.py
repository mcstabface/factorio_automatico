from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Literal

from artifacts.run_artifact_writer import RunArtifactWriter
from contracts.actions import Action
from contracts.artifacts import (
    ActionExecutionResult,
    MovementTransitionArtifact,
    PostExecutionObservation,
    RunAudit,
    TerminalTraceArtifact,
    TerminalTraceEvent,
)
from contracts.world_state import Position
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


def _serialize_for_return(payload: Any) -> dict[str, Any]:
    if not is_dataclass(payload):
        raise TypeError("Return payload must be a dataclass instance")
    return json.loads(json.dumps(asdict(payload)))


def _build_movement_transition(
    raw_state: dict[str, Any],
    execution_result: ActionExecutionResult,
    post_execution_observation: PostExecutionObservation,
) -> MovementTransitionArtifact:
    player_position = raw_state["player"]["position"]
    before_position = Position(
        x=float(player_position["x"]),
        y=float(player_position["y"]),
    )

    return MovementTransitionArtifact(
        before_position=before_position,
        requested_target_position=execution_result.target_position,
        after_position=post_execution_observation,
    )


def _build_terminal_trace(
    *,
    normalization_result: Any,
    action_validation_result: Any,
    execution_result: ActionExecutionResult,
    post_execution_observation: PostExecutionObservation,
    movement_transition: MovementTransitionArtifact,
    executor_type: Literal["stub", "factorio"],
) -> TerminalTraceArtifact:
    return TerminalTraceArtifact(
        title="Factorio MES Single Action Trace",
        mode=executor_type,
        summary=(
            f"{execution_result.action_type.value} "
            f"{execution_result.execution_status} via {execution_result.executor_name}"
        ),
        events=[
            TerminalTraceEvent(
                step="state_normalization",
                status="success",
                message="World state normalized",
                payload={
                    "tick": normalization_result.world_state.tick,
                },
            ),
            TerminalTraceEvent(
                step="action_validation",
                status="success",
                message="Candidate action validated",
                payload={
                    "action_id": action_validation_result.action.action_id,
                    "action_type": action_validation_result.action.action_type.value,
                },
            ),
            TerminalTraceEvent(
                step=f"{executor_type}_execution",
                status=execution_result.execution_status,
                message="Executor processed bounded action",
                payload={
                    "executor_name": execution_result.executor_name,
                    "target_position": asdict(execution_result.target_position),
                    "movement_started": execution_result.observed_result.movement_started,
                    "movement_completed": execution_result.observed_result.movement_completed,
                },
            ),
            TerminalTraceEvent(
                step="post_execution_observation",
                status="success",
                message="Post-execution observation captured",
                payload=_serialize_for_return(post_execution_observation),
            ),
            TerminalTraceEvent(
                step="movement_transition",
                status="success",
                message="Movement transition summarized",
                payload=_serialize_for_return(movement_transition),
            ),
        ],
    )


def _emit_terminal_trace(trace: TerminalTraceArtifact) -> None:
    print(f"\n=== {trace.title} ({trace.mode}) ===")
    print(trace.summary)
    for event in trace.events:
        print(f"[{event.status}] {event.step}: {event.message}")
        if event.payload is not None:
            print(json.dumps(event.payload, indent=2, sort_keys=True))


def run_single_action(
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    executor_type: Literal["stub", "factorio"] = "stub",
    run_id: str = RUN_ID,
    raw_state: dict[str, Any] | None = None,
    candidate_action: Action | dict[str, Any] | None = None,
    emit_terminal_trace: bool = False,
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
    post_execution_observation: PostExecutionObservation = (
        executor.observe_player_position()
    )
    movement_transition = _build_movement_transition(
        raw_state=raw_state,
        execution_result=execution_result,
        post_execution_observation=post_execution_observation,
    )
    terminal_trace = _build_terminal_trace(
        normalization_result=normalization_result,
        action_validation_result=action_validation_result,
        execution_result=execution_result,
        post_execution_observation=post_execution_observation,
        movement_transition=movement_transition,
        executor_type=executor_type,
    )

    run_audit = RunAudit(
        run_id=run_id,
        pipeline=[
            "state_normalization",
            "action_validation",
            f"{executor_type}_execution",
            "post_execution_observation",
            "artifact_write",
        ],
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
        post_execution_observation=post_execution_observation,
        movement_transition=movement_transition,
        terminal_trace=terminal_trace,
        run_audit=run_audit,
    )

    if emit_terminal_trace:
        _emit_terminal_trace(terminal_trace)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "executor_type": executor_type,
        "validated_action": asdict(action_validation_result.action),
        "execution_result": asdict(execution_result),
        "post_execution_observation": _serialize_for_return(
            post_execution_observation
        ),
        "movement_transition": _serialize_for_return(movement_transition),
        "terminal_trace": _serialize_for_return(terminal_trace),
        "run_audit": asdict(run_audit),
    }