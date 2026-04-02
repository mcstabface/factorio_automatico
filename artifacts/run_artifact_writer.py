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
        input_state_snapshot: dict[str, Any],
        state_normalization_debug: Any,
        validated_action: Any,
        action_validation_debug: Any,
        execution_result: dict[str, Any],
        run_audit: dict[str, Any],
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
        self._write_json(run_dir / "run_audit.json", run_audit)

        return run_dir

    def _write_json(self, path: Path, payload: Any) -> None:
        if is_dataclass(payload):
            serialized = asdict(payload)
        else:
            serialized = payload

        path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True),
            encoding="utf-8",
        )
