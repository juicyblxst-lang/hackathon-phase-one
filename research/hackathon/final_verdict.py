#!/usr/bin/env python3

import json
import os
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_verdict(run_dir):
    records = os.path.join(run_dir, "records")

    requirements = load_json(
        os.path.join(records, "requirement_verification.json")
    )

    repo = load_json(
        os.path.join(records, "repo_verification.json")
    )

    checks = requirements.get("checks", [])
    summary = requirements.get("summary", {})

    runtime = (
        repo.get("raw_evidence", {})
        .get("runtime_tests", {})
    )

    runtime_passed = runtime.get("status") == "PASS"

    failed = [
        check for check in checks
        if check.get("status") == "FAIL"
    ]

    review = [
        check for check in checks
        if check.get("status") == "REVIEW"
    ]

    agent_safety = [
        check for check in checks
        if check.get("category") == "agent_safety"
    ]

    agent_safety_passed = all(
        check.get("status") == "PASS"
        for check in agent_safety
    ) if agent_safety else False

    if failed:
        verdict = "FAIL"
        reason = "One or more requirements failed."

    elif not runtime_passed:
        verdict = "REVIEW"
        reason = "Runtime gate tests have not passed."

    elif not agent_safety_passed:
        verdict = "REVIEW"
        reason = "Agent-safety requirements are not fully verified."

    elif review:
        verdict = "REVIEW"
        reason = "Some requirements still require review."

    else:
        verdict = "PASS"
        reason = "All verified requirements passed deterministic checks."

    result = {
        "status": "FINAL_VERDICT",
        "verdict": verdict,
        "reason": reason,
        "summary": {
            "total_requirements": len(checks),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "review": summary.get("review", 0),
        },
        "runtime_gate": {
            "status": runtime.get("status"),
            "passed": runtime_passed,
            "returncode": runtime.get("returncode"),
        },
        "agent_safety": {
            "requirements": len(agent_safety),
            "passed": sum(
                x.get("status") == "PASS"
                for x in agent_safety
            ),
        },
        "failed_requirements": failed,
        "review_requirements": review,
    }

    output = os.path.join(records, "final_verdict.json")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result, output


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/final_verdict.py RUN_DIR"
        )
        sys.exit(1)

    result, output = build_verdict(sys.argv[1])

    print("FINAL VERDICT COMPLETE")
    print()
    print("VERDICT:", result["verdict"])
    print("Reason:", result["reason"])
    print()
    print("Requirements:", result["summary"]["total_requirements"])
    print("Passed:", result["summary"]["passed"])
    print("Failed:", result["summary"]["failed"])
    print("Review:", result["summary"]["review"])
    print()
    print(
        "Runtime gate:",
        result["runtime_gate"]["status"],
    )
    print(
        "Agent safety:",
        result["agent_safety"]["passed"],
        "/",
        result["agent_safety"]["requirements"],
    )
    print()
    print("Saved:", output)


if __name__ == "__main__":
    main()
