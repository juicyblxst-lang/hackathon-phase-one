def runtime_status(runtime):
    return {
        "status": "READY",
        "allowed_actions": sorted(runtime.gate.allowed_actions),
        "memory_path": str(runtime.memory.path),
    }


def action_status(action, result):
    return {
        "status": "EXECUTED",
        "action": action.get("action"),
        "result": result,
    }
