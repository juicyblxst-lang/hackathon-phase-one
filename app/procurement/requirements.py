class RequirementStore:
    """Structured requirements consumed by the agent workflow."""

    def __init__(self):
        self._requirements = []

    def add(self, requirement):
        if not isinstance(requirement, dict):
            raise ValueError("Requirement must be a dictionary.")

        name = requirement.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Requirement needs a name.")

        item = {
            "name": name.strip(),
            "description": str(requirement.get("description", "")).strip(),
            "required": bool(requirement.get("required", True)),
        }

        self._requirements.append(item)
        return item

    def all(self):
        return list(self._requirements)

    def required(self):
        return [
            requirement
            for requirement in self._requirements
            if requirement["required"]
        ]

    def clear(self):
        self._requirements.clear()
