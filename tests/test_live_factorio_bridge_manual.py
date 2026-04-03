from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from integrations.factorio.factorio_client import FactorioClient


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_FACTORIO_TESTS") != "1",
    reason="set RUN_LIVE_FACTORIO_TESTS=1 to run live Factorio bridge tests",
)


def test_live_factorio_bridge_moves_player() -> None:
    client = FactorioClient()

    before_position = client.get_player_position()

    target_x = before_position.x + 5.0
    target_y = before_position.y + 5.0

    move_result = client.move_to(target_x, target_y)
    after_position = client.get_player_position()

    assert move_result.started is True
    assert move_result.completed is False
    assert move_result.command == "move_to"

    assert move_result.target_position.x == pytest.approx(target_x)
    assert move_result.target_position.y == pytest.approx(target_y)

    assert (
        after_position.x != before_position.x
        or after_position.y != before_position.y
    ), (
        f"expected live move to change position, but before={before_position} "
        f"and after={after_position}"
    )

    assert abs(after_position.x - before_position.x) > 0.0
    assert abs(after_position.y - before_position.y) > 0.0


def test_live_walk_to_target_script_changes_position() -> None:
    client = FactorioClient()
    before_position = client.get_player_position()

    target_x = before_position.x + 8.0
    target_y = before_position.y + 8.0

    completed_process = subprocess.run(
        [
            sys.executable,
            "scripts/run_live_factorio_walk_to_target.py",
            str(target_x),
            str(target_y),
            "0.75",
            "12",
            "0.05",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed_process.stdout.strip(), "expected JSON summary on stdout"

    try:
        summary = json.loads(completed_process.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"expected JSON stdout, got: {completed_process.stdout!r}"
        ) from exc

    assert summary["status"] in {"target_reached", "max_steps_reached", "stuck_no_progress"}, (
        f"unexpected live walk status: {summary}"
    )
    assert summary["steps_taken"] >= 1, f"expected at least one step: {summary}"

    after_position = client.get_player_position()

    assert (
        after_position.x != before_position.x
        or after_position.y != before_position.y
    ), (
        "expected walk-to-target script to change live position, "
        f"but before={before_position} and after={after_position}; "
        f"summary={summary}"
    )