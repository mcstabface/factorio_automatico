from __future__ import annotations

import pytest

from contracts.actions import Action, ActionType
from contracts.artifacts import ActionExecutionResult
from executors.factorio_move_executor import FactorioMoveExecutor


class MockFactorioClient:
    def __init__(self) -> None:
        self.calls: list[tuple[float, float]] = []

    def move_to(self, x: float, y: float) -> dict[str, object]:
        self.calls.append((x, y))
        return {
            "started": True,
            "completed": False,
            "command": "move_to",
            "target_position": {"x": x, "y": y},
        }


def test_move_to_calls_adapter_with_exact_coordinates() -> None:
    client = MockFactorioClient()
    executor = FactorioMoveExecutor(client)
    action = Action(
        action_id="move-1",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 12.5, "y": -4.0}},
        preconditions=(),
        expected_effects=(),
    )

    executor.execute(action)

    assert client.calls == [(12.5, -4.0)]


def test_unsupported_action_types_fail_explicitly() -> None:
    client = MockFactorioClient()
    executor = FactorioMoveExecutor(client)
    action = Action(
        action_id="noop-1",
        action_type=ActionType.NO_OP,
        params={},
        preconditions=(),
        expected_effects=(),
    )

    with pytest.raises(ValueError, match="supports only MOVE_TO"):
        executor.execute(action)


def test_execution_result_shape_is_stable_and_deterministic() -> None:
    client = MockFactorioClient()
    executor = FactorioMoveExecutor(client)
    action = Action(
        action_id="move-2",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 1.0, "y": 2.0}},
        preconditions=("validated",),
        expected_effects=("movement requested",),
    )

    result = executor.execute(action)

    assert isinstance(result, ActionExecutionResult)
    assert result.success is True
    assert result.executor_name == "factorio_move_executor"
    assert result.action_id == "move-2"
    assert result.action_type is ActionType.MOVE_TO
    assert result.execution_status == "accepted"
    assert result.target_position.x == 1.0
    assert result.target_position.y == 2.0
    assert result.observed_result.movement_started is True
    assert result.observed_result.movement_completed is False
    assert result.error_message is None