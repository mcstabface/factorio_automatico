from __future__ import annotations

from dataclasses import dataclass

from contracts.actions import ActionType
from contracts.world_state import Position


@dataclass(frozen=True, slots=True)
class RunArtifactMetadata:
    run_id: str
    tick: int
    expert_name: str
    artifact_type: str
    created_at_utc: str


@dataclass(frozen=True, slots=True)
class MovementObservation:
    movement_started: bool
    movement_completed: bool


@dataclass(frozen=True, slots=True)
class ActionExecutionResult:
    success: bool
    executor_name: str
    action_id: str
    action_type: ActionType
    execution_status: str
    target_position: Position
    observed_result: MovementObservation
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class RunAudit:
    run_id: str
    pipeline: tuple[str, ...]
    executor_type: str
    status: str