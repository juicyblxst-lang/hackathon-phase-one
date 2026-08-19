import json
import os
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    return " ".join(str(text).lower().split())


def requirement_category(text):
    t = normalize(text)

    if any(x in t for x in [
        "deterministic gate",
        "rules the agent",
        "every action",
        "agent must follow",
    ]):
        return "agent_safety"

    if any(x in t for x in [
        "memory",
        "persist",
        "recall",
        "fresh session",
        "load-bearing",
    ]):
        return "memory"

    if any(x in t for x in [
        "base",
        "virtuals",
        "partner",
        "onchain",
        "transaction",
        "wallet",
    ]):
        return "partner"

    if any(x in t for x in [
        "deploy",
        "deployment",
        "live",
        "production",
    ]):
        return "deployment"

    if any(x in t for x in [
        "github",
        "repository",
        "repo",
        "license",
        "commit",
    ]):
        return "repository"

    if any(x in t for x in [
        "demo",
        "video",
        "submit",
        "submission",
    ]):
        return "submission"

    if any(x in t for x in [
        "eligib",
        "age",
        "jurisdiction",
        "entrant",
    ]):
        return "eligibility"

    if any(x in t for x in [
        "deterministic gate",
        "rules the agent",
        "every action",
        "model and every action",
        "agent must follow",
        "agent safety",
    ]):
        return "agent_safety"

    return "general"


def evidence_strength(match):
    strength = normalize(match.get("strength", ""))

    if strength == "implementation":
        return 3

    if strength == "test":
        return 3

    if strength == "dependency":
        return 1

    if strength == "signal":
        return 1

    if strength == "weak":
        return 0

    return 0


def is_relevant(match, category):
    evidence_category = normalize(match.get("category", ""))

    if category == "agent_safety":
        return evidence_category in {
            "agent_safety",
            "agent_safety_tests",
            "tests",
            "implementation",
        }

    if category == "memory":
        return evidence_category in {
            "memory",
            "integration_signals",
            "tests",
        }

    if category == "partner":
        return evidence_category in {
            "base",
            "virtuals",
            "partner",
            "integration_signals",
        }

    if category == "deployment":
        return evidence_category in {
            "deployment",
            "implementation",
            "integration_signals",
        }

    if category == "repository":
        return evidence_category in {
            "repository",
            "implementation",
        }

    if category == "submission":
        return evidence_category in {
            "submission",
            "documentation",
        }

    if category == "eligibility":
        return evidence_category in {
            "eligibility",
            "documentation",
        }

    if category == "agent_safety":
        return evidence_category in {
            "agent_safety",
            "implementation",
            "tests",
            "documentation",
        }

    return False


def verify_requirement(requirement, evidence):
    text = requirement.get("text", "")
    category = requirement_category(text)

    matches = [
        match
        for match in evidence
        if is_relevant(match, category)
    ]

    # For agent-safety requirements, prefer actual runtime gate execution
    # over references to the words "deterministic gate" elsewhere in the
    # verification system.
    if category == "agent_safety":
        runtime_matches = [
            match
            for match in matches
            if match.get("pattern") == "runtime_gate_execution"
            and match.get("strength") == "test"
        ]

        if runtime_matches:
            matches = runtime_matches

    strong_matches = [
        match
        for match in matches
        if evidence_strength(match) >= 2
    ]

    if not matches:
        status = "FAIL"
        reason = "No repository evidence matched this requirement."

    elif strong_matches:
        status = "PASS"
        reason = (
            "Repository contains implementation or test evidence "
            "relevant to this requirement."
        )

    else:
        status = "REVIEW"
        reason = (
            "Repository contains related signals, but no strong "
            "implementation/test evidence was found."
        )

    return {
        "fact_id": requirement.get("fact_id"),
        "requirement": text,
        "category": category,
        "status": status,
        "reason": reason,
        "evidence_count": len(matches),
        "strong_evidence_count": len(strong_matches),
        "evidence": matches[:10],
    }


def verify_requirements(requirements, evidence):
    checks = [
        verify_requirement(requirement, evidence)
        for requirement in requirements
    ]

    passed = sum(
        1 for check in checks
        if check["status"] == "PASS"
    )

    failed = sum(
        1 for check in checks
        if check["status"] == "FAIL"
    )

    review = sum(
        1 for check in checks
        if check["status"] == "REVIEW"
    )

    return {
        "status": "VERIFIED",
        "summary": {
            "total_requirements": len(checks),
            "passed": passed,
            "failed": failed,
            "review": review,
        },
        "checks": checks,
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/verify_requirements.py RUN_DIR"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    validated_path = os.path.join(
        run_dir,
        "records",
        "validated.json",
    )

    evidence_path = os.path.join(
        run_dir,
        "records",
        "evidence_classification.json",
    )

    output_path = os.path.join(
        run_dir,
        "records",
        "requirement_verification.json",
    )

    validated = load_json(validated_path)
    evidence_data = load_json(evidence_path)

    requirements = [
        fact
        for fact in validated.get("facts", [])
        if fact.get("fact_type") == "requirement"
    ]

    evidence = evidence_data.get("evidence", [])

    result = verify_requirements(
        requirements,
        evidence,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("REQUIREMENT VERIFICATION COMPLETE")
    print()
    print(
        "Requirements:",
        result["summary"]["total_requirements"],
    )
    print(
        "Passed:",
        result["summary"]["passed"],
    )
    print(
        "Failed:",
        result["summary"]["failed"],
    )
    print(
        "Review:",
        result["summary"]["review"],
    )
    print()
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
