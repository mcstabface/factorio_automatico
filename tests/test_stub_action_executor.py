from __future__ import annotations

import pytest

from contracts.actions import Action, ActionType
from contracts.artifacts import (
    ActionExecutionResult,
    StubObservationUnavailable,
)
from executors.stub_action_executor import StubActionExecutor


def test_stub_executor_execution_result_shape_is_stable_and_deterministic() -> None:
    executor = StubActionExecutor()
    action = Action(
        action_id="move-1",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 5.0, "y": 3.0}},
        preconditions=("validated",),
        expected_effects=("movement requested",),
    )

    result = executor.execute(action)

    assert isinstance(result, ActionExecutionResult)
    assert result.success is True
    assert result.executor_name == "stub_action_executor"
    assert result.action_id == "move-1"
    assert result.action_type is ActionType.MOVE_TO
    assert result.execution_status == "accepted"
    assert result.target_position.x == 5.0
    assert result.target_position.y == 3.0
    assert result.observed_result.movement_started is True
    assert result.observed_result.movement_completed is False
    assert result.error_message is None


def test_stub_executor_unsupported_action_types_fail_explicitly() -> None:
    executor = StubActionExecutor()
    action = Action(
        action_id="noop-1",
        action_type=ActionType.NO_OP,
        params={},
        preconditions=(),
        expected_effects=(),
    )

    with pytest.raises(ValueError, match="supports only MOVE_TO"):
        executor.execute(action)


def test_observe_player_position_returns_stable_stub_observation() -> None:
    executor = StubActionExecutor()

    observation = executor.observe_player_position()

    assert isinstance(observation, StubObservationUnavailable)
    assert observation.observation_type == "stub"
    assert observation.status == "not_available"
    assert observation.reason == "stub executor does not provide live game observation"