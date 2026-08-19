import pytest


class DeterministicGate:
    """
    Reference contract for the system's action gate.

    The model proposes an action.
    The gate deterministically validates it.
    Only an approved action reaches the executor.
    """

    def __init__(self, allowed_actions):
        self.allowed_actions = set(allowed_actions)

    def check(self, action):
        if not isinstance(action, dict):
            return False

        name = action.get("name")

        if not name:
            return False

        return name in self.allowed_actions


class ActionExecutor:
    def __init__(self):
        self.executed = []

    def execute(self, action):
        self.executed.append(action)
        return {"status": "executed", "action": action}


def guarded_execute(model_action, gate, executor):
    """
    Required architecture:

        model output
             ↓
        deterministic gate
             ↓
          executor
    """

    if not gate.check(model_action):
        return {
            "status": "blocked",
            "action": model_action,
        }

    return executor.execute(model_action)


def test_allowed_action_reaches_executor():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    result = guarded_execute(
        {"name": "search", "query": "hackathons"},
        gate,
        executor,
    )

    assert result["status"] == "executed"
    assert len(executor.executed) == 1


def test_disallowed_action_is_blocked():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    result = guarded_execute(
        {"name": "delete_database"},
        gate,
        executor,
    )

    assert result["status"] == "blocked"
    assert executor.executed == []


def test_malformed_model_output_is_blocked():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    result = guarded_execute(
        {"query": "hackathons"},
        gate,
        executor,
    )

    assert result["status"] == "blocked"
    assert executor.executed == []


def test_non_dict_model_output_is_blocked():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    result = guarded_execute(
        "execute whatever",
        gate,
        executor,
    )

    assert result["status"] == "blocked"
    assert executor.executed == []


def test_every_action_must_pass_gate():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    actions = [
        {"name": "search"},
        {"name": "delete_database"},
        {"name": "search"},
        {"name": "transfer_funds"},
    ]

    for action in actions:
        guarded_execute(action, gate, executor)

    assert executor.executed == [
        {"name": "search"},
        {"name": "search"},
    ]
