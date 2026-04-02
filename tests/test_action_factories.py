from __future__ import annotations

from contracts.actions import Action, ActionType


def test_action_move_to_factory_builds_expected_action() -> None:
    action = Action.move_to(
        action_id="move-demo-001",
        x=9.0,
        y=7.0,
        preconditions=("world state is normalized",),
        expected_effects=("player target position is echoed by executor",),
    )

    assert action.action_id == "move-demo-001"
    assert action.action_type is ActionType.MOVE_TO
    assert action.params == {"target_position": {"x": 9.0, "y": 7.0}}
    assert action.preconditions == ("world state is normalized",)
    assert action.expected_effects == ("player target position is echoed by executor",)