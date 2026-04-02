from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


class RunArtifactWriter:
    def __init__(self, artifact_root: str | Path) -> None:
        self.artifact_root = Path(artifact_root)

    def write_run_artifacts(
        self,
        *,
        run_id: str,
        input_state_snapshot: Any,
        state_normalization_debug: Any,
        validated_action: Any,
        action_validation_debug: Any,
        execution_result: Any,
        run_audit: Any,
        post_execution_observation: Any | None = None,
        movement_transition: Any | None = None,
        terminal_trace: Any | None = None,
    ) -> Path:
        run_dir = self.artifact_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_json(run_dir / "input_state_snapshot.json", input_state_snapshot)
        self._write_json(
            run_dir / "state_normalization_debug.json", state_normalization_debug
        )
        self._write_json(run_dir / "validated_action.json", validated_action)
        self._write_json(
            run_dir / "action_validation_debug.json", action_validation_debug
        )
        self._write_json(run_dir / "execution_result.json", execution_result)

        if post_execution_observation is not None:
            self._write_json(
                run_dir / "post_execution_observation.json",
                post_execution_observation,
            )

        if movement_transition is not None:
            self._write_json(
                run_dir / "movement_transition.json",
                movement_transition,
            )

        if terminal_trace is not None:
            self._write_json(
                run_dir / "terminal_trace.json",
                terminal_trace,
            )

        self._write_json(run_dir / "run_audit.json", run_audit)

        return run_dir

    def _serialize_payload(self, payload: Any) -> Any:
        if is_dataclass(payload):
            return asdict(payload)
        return payload

    def _write_json(self, path: Path, payload: Any) -> None:
        serialized = self._serialize_payload(payload)
        path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True),
            encoding="utf-8",
        )