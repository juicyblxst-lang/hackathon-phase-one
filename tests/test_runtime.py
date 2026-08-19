import tempfile
import unittest

from app.agent.runtime import AgentRuntime


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.runtime = AgentRuntime(
            allowed_actions={"remember", "recall"},
            memory_path=self.tmp.name,
        )

    def test_memory_round_trip(self):
        self.runtime.execute({
            "action": "remember",
            "key": "test",
            "value": "hello",
        })

        result = self.runtime.execute({
            "action": "recall",
            "key": "test",
        })

        self.assertEqual(result["value"], "hello")

    def test_gate_blocks_unknown_action(self):
        with self.assertRaises(PermissionError):
            self.runtime.execute({
                "action": "delete_everything",
            })

    def test_malformed_action_blocked(self):
        with self.assertRaises(PermissionError):
            self.runtime.execute("not-an-action")


    def test_base_action_passes_through_gate(self):
        self.runtime.gate.allowed_actions = frozenset(
            {"remember", "recall", "base_execute"}
        )

        result = self.runtime.execute({
            "action": "base_execute",
            "operation": "test_transaction",
            "payload": {"value": 123},
        })

        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["operation"], "test_transaction")
        self.assertEqual(result["payload"]["value"], 123)



if __name__ == "__main__":
    unittest.main()
