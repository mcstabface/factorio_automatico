from __future__ import annotations

import os

import pytest

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