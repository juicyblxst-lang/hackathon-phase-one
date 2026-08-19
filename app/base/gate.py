class DeterministicGate:
    """Deterministic allow/deny gate for every agent action."""

    def __init__(self, allowed_actions):
        self.allowed_actions = frozenset(allowed_actions)

    def validate(self, action):
        if not isinstance(action, dict):
            raise PermissionError("Malformed action blocked.")

        name = action.get("action")

        if not isinstance(name, str) or not name:
            raise PermissionError("Malformed action blocked.")

        if name not in self.allowed_actions:
            raise PermissionError(f"Action not allowed: {name}")

        return action

    def execute(self, action, handlers):
        action = self.validate(action)

        name = action["action"]
        handler = handlers.get(name)

        if handler is None:
            raise RuntimeError(f"No handler registered for action: {name}")

        return handler(action)


Gate = DeterministicGate
