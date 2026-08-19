import unittest

from app.procurement.requirements import RequirementStore


class ProcurementTests(unittest.TestCase):

    def test_add_and_retrieve_requirement(self):
        store = RequirementStore()

        result = store.add({
            "name": "Memory",
            "description": "Persistent context",
            "required": True,
        })

        self.assertEqual(result["name"], "Memory")
        self.assertEqual(len(store.all()), 1)
        self.assertEqual(len(store.required()), 1)

    def test_optional_requirement(self):
        store = RequirementStore()

        store.add({
            "name": "Base",
            "required": False,
        })

        self.assertEqual(len(store.all()), 1)
        self.assertEqual(len(store.required()), 0)

    def test_invalid_requirement_blocked(self):
        store = RequirementStore()

        with self.assertRaises(ValueError):
            store.add("not-a-requirement")


if __name__ == "__main__":
    unittest.main()
