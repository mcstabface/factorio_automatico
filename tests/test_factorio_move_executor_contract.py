from __future__ import annotations

import pytest

from contracts.actions import Action, ActionType
from contracts.artifacts import ActionExecutionResult
from contracts.world_state import Position
from executors.factorio_move_executor import FactorioMoveExecutor
from integrations.factorio.factorio_client import MoveToCommandResult


class MockFactorioClient:
    def __init__(self) -> None:
        self.calls: list[tuple[float, float]] = []
        self.observation_calls = 0
        self.player_position = Position(x=0.0, y=0.0)

    def move_to(self, x: float, y: float) -> MoveToCommandResult:
        self.calls.append((x, y))
        self.player_position = Position(x=x, y=y)
        return MoveToCommandResult(
            started=True,
            completed=True,
            command="move_to",
            target_position=Position(x=x, y=y),
        )

    def get_player_position(self) -> Position:
        self.observation_calls += 1
        return self.player_position


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
    assert result.observed_result.movement_completed is True
    assert result.error_message is None


def test_observe_player_position_delegates_to_factorio_client() -> None:
    client = MockFactorioClient()
    executor = FactorioMoveExecutor(client)

    observed_position = executor.observe_player_position()

    assert observed_position == Position(x=0.0, y=0.0)
    assert client.observation_calls == 1


def test_execute_changes_observed_player_position() -> None:
    client = MockFactorioClient()
    executor = FactorioMoveExecutor(client)
    action = Action(
        action_id="move-3",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 5.0, "y": 3.0}},
        preconditions=(),
        expected_effects=(),
    )

    before_position = executor.observe_player_position()
    executor.execute(action)
    after_position = executor.observe_player_position()

    assert before_position == Position(x=0.0, y=0.0)
    assert after_position == Position(x=5.0, y=3.0)
    assert client.calls == [(5.0, 3.0)]
    assert client.observation_calls == 2


def test_execution_result_preserves_incomplete_adapter_state() -> None:
    class IncompleteMoveFactorioClient(MockFactorioClient):
        def move_to(self, x: float, y: float) -> MoveToCommandResult:
            self.calls.append((x, y))
            self.player_position = Position(x=x - 1.0, y=y - 1.0)
            return MoveToCommandResult(
                started=True,
                completed=False,
                command="move_to",
                target_position=Position(x=x, y=y),
            )

    client = IncompleteMoveFactorioClient()
    executor = FactorioMoveExecutor(client)
    action = Action(
        action_id="move-4",
        action_type=ActionType.MOVE_TO,
        params={"target_position": {"x": 9.0, "y": 4.0}},
        preconditions=(),
        expected_effects=(),
    )

    result = executor.execute(action)

    assert result.success is True
    assert result.execution_status == "accepted"
    assert result.observed_result.movement_started is True
    assert result.observed_result.movement_completed is False
    assert result.target_position == Position(x=9.0, y=4.0)
    assert client.calls == [(9.0, 4.0)]