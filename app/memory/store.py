import json
from pathlib import Path


class MemoryStore:
    """Small persistent JSON memory store."""

    def __init__(self, path="data/memory.json"):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return {}

        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

        return data if isinstance(data, dict) else {}

    def save(self, memories):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        tmp = self.path.with_suffix(self.path.suffix + ".tmp")

        with tmp.open("w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)

        tmp.replace(self.path)

    def remember(self, key, value):
        if not isinstance(key, str) or not key:
            raise ValueError("Memory key must be a non-empty string.")

        memories = self.load()
        memories[key] = value
        self.save(memories)

        return {
            "status": "remembered",
            "key": key,
            "value": value,
        }

    def recall(self, key):
        memories = self.load()

        return {
            "status": "recalled",
            "key": key,
            "value": memories.get(key),
            "found": key in memories,
        }
