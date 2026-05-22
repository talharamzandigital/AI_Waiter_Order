from enum import Enum


class OrderState(Enum):
    """All possible states of an order session."""
    NEW = "new"
    COLLECTING = "collecting"
    CONFIRMED = "confirmed"
    PLACED = "placed"
    CANCELLED = "cancelled"


# ── Allowed transitions ───────────────────────────────────────
TRANSITIONS = {
    OrderState.NEW: [OrderState.COLLECTING, OrderState.CANCELLED],
    OrderState.COLLECTING: [OrderState.CONFIRMED, OrderState.CANCELLED],
    OrderState.CONFIRMED: [OrderState.PLACED, OrderState.COLLECTING],
    OrderState.PLACED: [],
    OrderState.CANCELLED: [],
}


class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class OrderStateMachine:
    """Controls the order flow — no skipping allowed!"""

    def __init__(self, current_state=None):
        self.state = current_state or OrderState.NEW

    def can_transition(self, new_state):
        """Check if transition is allowed."""
        return new_state in TRANSITIONS.get(self.state, [])

    def transition(self, new_state):
        """Move to new state — raises error if not allowed."""
        if not self.can_transition(new_state):
            raise StateMachineError(
                f"Cannot move from '{self.state.value}' "
                f"to '{new_state.value}'. "
                f"Allowed transitions: "
                f"{[s.value for s in TRANSITIONS.get(self.state, [])]}"
            )
        old_state = self.state
        self.state = new_state
        return old_state, new_state

    def is_collecting(self):
        return self.state == OrderState.COLLECTING

    def is_confirmed(self):
        return self.state == OrderState.CONFIRMED

    def is_placed(self):
        return self.state == OrderState.PLACED

    def is_cancelled(self):
        return self.state == OrderState.CANCELLED

    def get_allowed_transitions(self):
        """Return list of allowed next states."""
        return [s.value for s in TRANSITIONS.get(self.state, [])]

    def __str__(self):
        return f"OrderStateMachine(state={self.state.value})"