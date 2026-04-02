from __future__ import annotations

from dataclasses import dataclass

from contracts.actions import Action


@dataclass(frozen=True, slots=True)
class ExpertDebugArtifact:
    run_id: str
    expert_name: str
    tick: int
    success: bool
    summary: str
    considered_facts: tuple[str, ...]
    proposed_actions: tuple[Action, ...]
    warnings: tuple[str, ...] = ()
    error_message: str | None = None
    duration_ms: int = 0
    input_ref: str | None = None
    output_ref: str | None = None