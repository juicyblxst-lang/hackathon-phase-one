import tempfile
import unittest
from pathlib import Path

from app.agent.runtime import AgentRuntime
from app.base.client import BaseClient


class EndToEndTests(unittest.TestCase):

    def test_agent_memory_and_gate_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = AgentRuntime(
                allowed_actions={"remember", "recall"},
                memory_path=str(Path(tmp) / "memory.json"),
            )

            saved = runtime.execute({
                "action": "remember",
                "key": "user_goal",
                "value": "ship the system",
            })

            self.assertEqual(saved["status"], "remembered")

            recalled = runtime.execute({
                "action": "recall",
                "key": "user_goal",
            })

            self.assertTrue(recalled["found"])
            self.assertEqual(recalled["value"], "ship the system")

    def test_disallowed_action_never_reaches_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = AgentRuntime(
                allowed_actions={"remember", "recall"},
                memory_path=str(Path(tmp) / "memory.json"),
            )

            with self.assertRaises(PermissionError):
                runtime.execute({
                    "action": "send_transaction",
                    "transaction": {"to": "test"},
                })

    def test_base_client_is_safe_by_default(self):
        client = BaseClient()

        result = client.send_transaction({
            "to": "test",
            "value": 0,
        })

        self.assertEqual(result["status"], "dry_run")


if __name__ == "__main__":
    unittest.main()
