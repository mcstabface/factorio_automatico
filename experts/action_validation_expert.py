from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contracts.actions import Action
from contracts.expert_debug import ExpertDebugArtifact
from contracts.world_state import WorldState
from validation.action_validator import validate_action
from validation.state_validator import validate_world_state


@dataclass(frozen=True, slots=True)
class ActionValidationResult:
    action: Action
    debug_artifact: ExpertDebugArtifact


class ActionValidationExpert:
    expert_name = "action_validation_expert"

    def run(
        self,
        candidate_action: Action | dict[str, Any],
        world_state: WorldState | dict[str, Any],
        run_id: str,
    ) -> ActionValidationResult:
        normalized_world_state = validate_world_state(world_state)
        action = validate_action(candidate_action, normalized_world_state)
        debug_artifact = ExpertDebugArtifact(
            run_id=run_id,
            expert_name=self.expert_name,
            tick=normalized_world_state.tick,
            success=True,
            summary="Candidate action validated against normalized world state.",
            considered_facts=(
                f"action_type={action.action_type.value}",
                f"tick={normalized_world_state.tick}",
                f"objective={normalized_world_state.objective.current_goal or 'NONE'}",
            ),
            proposed_actions=(action,),
            warnings=(),
            error_message=None,
            duration_ms=0,
            input_ref=None,
            output_ref=None,
        )
        return ActionValidationResult(action=action, debug_artifact=debug_artifact)