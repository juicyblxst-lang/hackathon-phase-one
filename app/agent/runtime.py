from app.base.gate import DeterministicGate
from app.base.client import BaseClient
from app.memory.store import MemoryStore


class AgentRuntime:
    """Agent execution runtime.

    All actions pass through the deterministic gate before execution.
    """

    def __init__(
        self,
        allowed_actions=None,
        memory_path="data/memory.json",
        handlers=None,
    ):
        allowed_actions = allowed_actions or {
            "remember",
            "recall",
        }

        self.gate = DeterministicGate(allowed_actions)
        self.memory = MemoryStore(memory_path)
        self.base = BaseClient()

        default_handlers = {
            "base_execute": lambda action: self.base.execute(action),
            "remember": lambda action: self.remember(
                action["key"],
                action.get("value"),
            ),
            "recall": lambda action: self.recall(
                action["key"],
            ),
        }

        if handlers:
            default_handlers.update(handlers)

        self.handlers = default_handlers

    def remember(self, key, value):
        return self.memory.remember(key, value)

    def recall(self, key):
        return self.memory.recall(key)

    def execute(self, action):
        return self.gate.execute(action, self.handlers)
