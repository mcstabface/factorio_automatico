from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contracts.expert_debug import ExpertDebugArtifact
from contracts.world_state import WorldState
from validation.state_validator import validate_world_state


@dataclass(frozen=True, slots=True)
class StateNormalizationResult:
    world_state: WorldState
    debug_artifact: ExpertDebugArtifact


class StateNormalizationExpert:
    expert_name = "state_normalization_expert"

    def run(self, raw_state: dict[str, Any], run_id: str) -> StateNormalizationResult:
        world_state = validate_world_state(raw_state)
        debug_artifact = ExpertDebugArtifact(
            run_id=run_id,
            expert_name=self.expert_name,
            tick=world_state.tick,
            success=True,
            summary="Raw mocked state normalized and validated.",
            considered_facts=(
                f"tick={world_state.tick}",
                f"inventory_items={len(world_state.player.inventory)}",
                f"nearby_resources={len(world_state.nearby_resources)}",
                f"nearby_entities={len(world_state.nearby_entities)}",
            ),
            proposed_actions=(),
            warnings=(),
            error_message=None,
            duration_ms=0,
            input_ref=None,
            output_ref=None,
        )
        return StateNormalizationResult(
            world_state=world_state,
            debug_artifact=debug_artifact,
        )
