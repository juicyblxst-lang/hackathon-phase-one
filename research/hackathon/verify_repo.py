import json
import os
import sys
import subprocess

from evidence_engine import inspect_project


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_runtime_tests(project_dir):
    test_file = os.path.join(project_dir, "tests", "run_gate_tests.py")

    if not os.path.isfile(test_file):
        return {
            "status": "NOT_FOUND",
            "command": ["python3", "tests/run_gate_tests.py"],
            "stdout": "",
            "stderr": "",
        }

    try:
        result = subprocess.run(
            ["python3", test_file],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "command": ["python3", "tests/run_gate_tests.py"],
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "command": ["python3", "tests/run_gate_tests.py"],
            "stdout": "",
            "stderr": "Gate tests exceeded 60 second timeout.",
        }


def verify_repo(run_dir, project_dir):
    facts = load_json(
        os.path.join(run_dir, "records", "validated.json")
    )

    evidence = inspect_project(project_dir)
    runtime_tests = run_runtime_tests(project_dir)

    evidence["runtime_tests"] = runtime_tests

    requirements = [
        fact for fact in facts.get("facts", [])
        if fact.get("fact_type") == "requirement"
    ]

    checks = []

    for requirement in requirements:
        text = requirement.get("text", "")
        lower = text.lower()

        if any(
            x in lower
            for x in [
                "deterministic gate",
                "rules the agent",
                "every action",
            ]
        ):
            implementation = evidence.get("agent_safety", {}).get("matches", [])
            tests = evidence.get("agent_safety_tests", {}).get("matches", [])

            matches = implementation + tests

            if implementation and tests:
                status = "PASS"
                reason = (
                    "Repository contains deterministic gate implementation "
                    "and executable tests demonstrating that actions are "
                    "blocked or executed through the gate."
                )
            elif tests:
                status = "REVIEW"
                reason = (
                    "Executable deterministic-gate tests exist, but the "
                    "production agent/action path is not implemented yet."
                )
            elif implementation:
                status = "REVIEW"
                reason = (
                    "Deterministic-gate implementation signals exist, but "
                    "executable enforcement tests were not found."
                )
            else:
                status = "FAIL"
                reason = (
                    "No deterministic gate implementation or executable "
                    "test evidence was found."
                )

        elif any(
            x in lower
            for x in ["memory", "persist", "recall", "load-bearing"]
        ):
            matches = evidence["memory"]["matches"]

            if matches:
                status = "REVIEW"
                reason = (
                    "Repository contains memory-related implementation "
                    "signals, but execution/load-bearing behavior is not "
                    "proven by static inspection."
                )
            else:
                status = "FAIL"
                reason = "No memory implementation evidence found."

        elif any(
            x in lower
            for x in ["base", "virtuals", "partner"]
        ):
            matches = evidence["base"]["matches"]

            if matches:
                status = "REVIEW"
                reason = (
                    "Repository contains partner/onchain signals, but "
                    "real integration execution is not proven."
                )
            else:
                status = "REVIEW"
                reason = "No partner integration implementation evidence found."

        elif any(
            x in lower
            for x in [
                "deterministic gate",
                "rules the agent",
                "every action",
                "model and every action",
                "agent must follow",
            ]
        ):
            matches = evidence["agent_safety"]["matches"]
            test_matches = evidence["agent_safety_tests"]["matches"]

            if matches and test_matches:
                status = "PASS"
                reason = (
                    "Repository contains deterministic agent-safety gate "
                    "implementation and executable tests covering allowed, "
                    "blocked, malformed, and repeated actions."
                )
            elif matches:
                status = "REVIEW"
                reason = (
                    "Agent-safety gate signals were found, but executable "
                    "tests proving enforcement are missing."
                )
            elif test_matches:
                status = "REVIEW"
                reason = (
                    "Agent-safety tests exist, but the repository does not "
                    "contain the corresponding production gate implementation."
                )
            else:
                status = "FAIL"
                reason = (
                    "No deterministic gate implementation was found between "
                    "the model and action execution."
                )

        elif any(
            x in lower
            for x in ["wrapper", "decorative", "real execution"]
        ):
            matches = evidence["integration_signals"]["matches"]

            status = "REVIEW"
            reason = (
                "Static inspection cannot establish meaningful runtime "
                "execution. Runtime tests are required."
            )

        else:
            matches = []
            status = "REVIEW"
            reason = "Requires additional project-level evidence."

        checks.append({
            "requirement": text,
            "status": status,
            "reason": reason,
            "repository_evidence": matches[:20],
        })

    result = {
        "status": "REPOSITORY_INSPECTED",
        "project_dir": os.path.abspath(project_dir),
        "summary": {
            "total_requirements": len(checks),
            "passed": sum(
                c["status"] == "PASS" for c in checks
            ),
            "failed": sum(
                c["status"] == "FAIL" for c in checks
            ),
            "review": sum(
                c["status"] == "REVIEW" for c in checks
            ),
        },
        "checks": checks,
        "raw_evidence": evidence,
    }

    output = os.path.join(
        run_dir,
        "records",
        "repo_verification.json",
    )

    save_json(output, result)

    print("REPOSITORY VERIFICATION COMPLETE")
    print()
    print("Requirements:", result["summary"]["total_requirements"])
    print("Passed:", result["summary"]["passed"])
    print("Failed:", result["summary"]["failed"])
    print("Review:", result["summary"]["review"])
    print()
    print("Saved:", output)


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 research/hackathon/verify_repo.py "
            "RUN_DIR PROJECT_DIR"
        )
        sys.exit(1)

    verify_repo(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
