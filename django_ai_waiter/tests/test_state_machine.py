import pytest
from django_ai_waiter.state_machine import (
    OrderStateMachine,
    OrderState,
    StateMachineError,
)


class TestStateMachine:

    def test_initial_state_is_new(self):
        sm = OrderStateMachine()
        assert sm.state == OrderState.NEW

    def test_new_to_collecting(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.COLLECTING)
        assert sm.state == OrderState.COLLECTING

    def test_collecting_to_confirmed(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.COLLECTING)
        sm.transition(OrderState.CONFIRMED)
        assert sm.state == OrderState.CONFIRMED

    def test_confirmed_to_placed(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.COLLECTING)
        sm.transition(OrderState.CONFIRMED)
        sm.transition(OrderState.PLACED)
        assert sm.state == OrderState.PLACED

    def test_cannot_skip_collecting(self):
        sm = OrderStateMachine()
        with pytest.raises(StateMachineError):
            sm.transition(OrderState.CONFIRMED)

    def test_cannot_skip_to_placed(self):
        sm = OrderStateMachine()
        with pytest.raises(StateMachineError):
            sm.transition(OrderState.PLACED)

    def test_cannot_go_back_from_placed(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.COLLECTING)
        sm.transition(OrderState.CONFIRMED)
        sm.transition(OrderState.PLACED)
        with pytest.raises(StateMachineError):
            sm.transition(OrderState.COLLECTING)

    def test_can_cancel_from_new(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.CANCELLED)
        assert sm.state == OrderState.CANCELLED

    def test_can_cancel_from_collecting(self):
        sm = OrderStateMachine()
        sm.transition(OrderState.COLLECTING)
        sm.transition(OrderState.CANCELLED)
        assert sm.state == OrderState.CANCELLED

    def test_get_allowed_transitions(self):
        sm = OrderStateMachine()
        allowed = sm.get_allowed_transitions()
        assert "collecting" in allowed
        assert "cancelled" in allowed