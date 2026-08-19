#!/usr/bin/env python3

import json
import os
import subprocess
import sys

from evidence_engine import inspect_project


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_command(project_dir, command, timeout=60):
    try:
        result = subprocess.run(
            command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "command": command,
            "stdout": "",
            "stderr": f"Command exceeded {timeout} second timeout.",
        }


def run_runtime_tests(project_dir):
    test_file = os.path.join(project_dir, "tests", "run_gate_tests.py")

    if not os.path.isfile(test_file):
        return {
            "status": "NOT_FOUND",
            "command": ["python3", "tests/run_gate_tests.py"],
            "stdout": "",
            "stderr": "",
        }

    return run_command(
        project_dir,
        ["python3", test_file],
        timeout=60,
    )


def run_full_tests(project_dir):
    tests_dir = os.path.join(project_dir, "tests")

    if not os.path.isdir(tests_dir):
        return {
            "status": "NOT_FOUND",
            "command": [
                "python3",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_*.py",
            ],
            "stdout": "",
            "stderr": "",
        }

    return run_command(
        project_dir,
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ],
        timeout=60,
    )


def is_noise_requirement(text):
    lower = text.lower().strip()

    noise_patterns = [
        "total prize pool",
        "what judges are looking for",
        "violations result in immediate disqualification",
        "do we need to deploy",
        "what are the mandatory submission requirements",
        "you must be logged in to block users",
        "you need to enable javascript",
        "no technical knowledge required",
        "get test tokens",
        "how to become a validator",
        "stake qie tokens",
        "minimum staking requirements",
        "you must be a member to see",
        "public display of winning projects",
        "qie ecosystem",
    ]

    return any(pattern in lower for pattern in noise_patterns)


def classify_requirement(text):
    lower = text.lower()

    if is_noise_requirement(text):
        return "NON_IMPLEMENTATION"

    if any(
        x in lower
        for x in [
            "deterministic gate",
            "every action",
            "rules the agent",
            "model and every action",
            "agent must follow",
        ]
    ):
        return "SAFETY_GATE"

    if any(
        x in lower
        for x in [
            "memory",
            "persist",
            "recall",
            "load-bearing",
        ]
    ):
        return "MEMORY"

    if any(
        x in lower
        for x in [
            "base",
            "qie blockchain",
            "qie ecosystem",
            "onchain",
            "on-chain",
            "wallet",
            "transaction",
            "qiedex",
            "oracle",
            "qie pass",
        ]
    ):
        return "INTEGRATION"

    if any(
        x in lower
        for x in [
            "working demo",
            "prototype",
            "functional demonstration",
            "runtime",
            "real execution",
        ]
    ):
        return "RUNTIME"

    if "github" in lower or "source code" in lower:
        return "SOURCE"

    if "documentation" in lower or "comprehensive documentation" in lower:
        return "DOCUMENTATION"

    if "original work" in lower or "original" in lower:
        return "ORIGINALITY"

    return "REVIEW"


def evidence_for_category(category, evidence, runtime_tests, full_tests):
    if category == "SAFETY_GATE":
        implementation = evidence.get(
            "agent_safety", {}
        ).get("matches", [])

        tests = evidence.get(
            "agent_safety_tests", {}
        ).get("matches", [])

        if implementation and tests and runtime_tests["status"] == "PASS":
            return (
                "PASS",
                (
                    "Deterministic safety-gate implementation and executable "
                    "tests were found, and the runtime gate suite passed."
                ),
                implementation + tests,
            )

        if implementation or tests:
            return (
                "REVIEW",
                (
                    "Safety-gate implementation/test evidence exists, but "
                    "the complete execution chain is not independently proven."
                ),
                implementation + tests,
            )

        return (
            "FAIL",
            "No deterministic safety-gate evidence was found.",
            [],
        )

    if category == "MEMORY":
        matches = evidence.get(
            "memory", {}
        ).get("matches", [])

        if matches:
            return (
                "REVIEW",
                (
                    "Memory implementation signals were found. Static "
                    "inspection does not independently prove persistent "
                    "load/recall behavior."
                ),
                matches,
            )

        return (
            "FAIL",
            "No memory implementation evidence was found.",
            [],
        )

    if category == "INTEGRATION":
        matches = evidence.get(
            "base", {}
        ).get("matches", [])

        if matches:
            return (
                "REVIEW",
                (
                    "Repository contains integration/onchain signals, but "
                    "a real QIE/Base transaction has not been independently "
                    "verified by this repository check."
                ),
                matches,
            )

        return (
            "REVIEW",
            "No executable onchain integration evidence was found.",
            [],
        )

    if category == "RUNTIME":
        if runtime_tests["status"] == "PASS":
            return (
                "PASS",
                "Runtime gate tests executed successfully.",
                [],
            )

        if full_tests["status"] == "PASS":
            return (
                "PASS",
                "Full repository test suite executed successfully.",
                [],
            )

        return (
            "REVIEW",
            "Runtime execution requires additional evidence.",
            [],
        )

    if category == "SOURCE":
        if os.path.isdir(".git"):
            return (
                "PASS",
                "Repository contains Git metadata and source files.",
                [],
            )

        return (
            "REVIEW",
            "Git/source repository evidence requires external submission verification.",
            [],
        )

    if category == "DOCUMENTATION":
        if os.path.isfile("README.md") or os.path.isdir("docs"):
            return (
                "PASS",
                "Repository contains project documentation.",
                [],
            )

        return (
            "REVIEW",
            "No project documentation was found.",
            [],
        )

    if category == "ORIGINALITY":
        return (
            "REVIEW",
            (
                "Originality cannot be established reliably from static "
                "repository inspection alone."
            ),
            [],
        )

    return (
        "REVIEW",
        "Requires additional project-level evidence.",
        [],
    )


def split_compound_submission_requirement(text):
    lower = text.lower()

    if "eligibility" not in lower:
        return [text]

    items = [
        "Must be built on or integrate with the QIE blockchain",
        "Must be original work created during the hackathon period",
        "Must include a working demo or prototype",
        "Must provide source code via GitHub repository",
        "Must include comprehensive documentation",
        "Must not violate any intellectual property rights",
    ]

    return items


def verify_repo(run_dir, project_dir):
    facts = load_json(
        os.path.join(run_dir, "records", "validated.json")
    )

    evidence = inspect_project(project_dir)

    runtime_tests = run_runtime_tests(project_dir)
    full_tests = run_full_tests(project_dir)

    evidence["runtime_tests"] = runtime_tests
    evidence["full_tests"] = full_tests

    raw_requirements = [
        fact
        for fact in facts.get("facts", [])
        if fact.get("fact_type") == "requirement"
    ]

    requirements = []

    for fact in raw_requirements:
        text = fact.get("text", "").strip()

        if not text:
            continue

        if is_noise_requirement(text):
            continue

        for item in split_compound_submission_requirement(text):
            if item not in requirements:
                requirements.append(item)

    checks = []

    for requirement in requirements:
        category = classify_requirement(requirement)

        status, reason, matches = evidence_for_category(
            category,
            evidence,
            runtime_tests,
            full_tests,
        )

        checks.append(
            {
                "requirement": requirement,
                "category": category,
                "status": status,
                "reason": reason,
                "repository_evidence": matches[:20],
            }
        )

    result = {
        "status": "REPOSITORY_INSPECTED",
        "project_dir": os.path.abspath(project_dir),
        "verification_version": "v2",
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
    print("Runtime tests:", runtime_tests["status"])
    print("Full tests:", full_tests["status"])
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
