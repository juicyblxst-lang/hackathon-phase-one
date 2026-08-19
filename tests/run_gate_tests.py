from test_deterministic_gate import (
    DeterministicGate,
    ActionExecutor,
    guarded_execute,
)


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    print("PASS:", name)


def main():
    gate = DeterministicGate({"search"})
    executor = ActionExecutor()

    result = guarded_execute(
        {"name": "search"},
        gate,
        executor,
    )
    check(
        "allowed action executes",
        result["status"] == "executed",
    )

    executor = ActionExecutor()

    result = guarded_execute(
        {"name": "delete_database"},
        gate,
        executor,
    )
    check(
        "disallowed action blocked",
        result["status"] == "blocked"
        and executor.executed == [],
    )

    executor = ActionExecutor()

    result = guarded_execute(
        {"query": "missing action name"},
        gate,
        executor,
    )
    check(
        "malformed action blocked",
        result["status"] == "blocked"
        and executor.executed == [],
    )

    executor = ActionExecutor()

    actions = [
        {"name": "search"},
        {"name": "delete_database"},
        {"name": "search"},
        {"name": "transfer_funds"},
    ]

    for action in actions:
        guarded_execute(action, gate, executor)

    check(
        "every action passes through gate",
        executor.executed == [
            {"name": "search"},
            {"name": "search"},
        ],
    )

    print()
    print("DETERMINISTIC GATE TESTS PASSED")


if __name__ == "__main__":
    main()
