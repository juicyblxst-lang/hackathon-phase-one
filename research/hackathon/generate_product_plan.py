#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def text(value):
    return str(value).strip() if value is not None else ""


def fact_id(fact, index):
    return (
        fact.get("fact_id")
        or fact.get("id")
        or f"requirement-{index:04d}"
    )


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/generate_product_plan.py RUN_DIR"
        )
        sys.exit(1)

    run_dir = Path(sys.argv[1]).resolve()
    records = run_dir / "records"

    validated_path = records / "validated.json"
    spec_path = records / "mvp_spec.json"

    if not validated_path.exists():
        print("ERROR: validated.json not found.")
        sys.exit(1)

    if not spec_path.exists():
        print("ERROR: mvp_spec.json not found.")
        sys.exit(1)

    validated = load(validated_path)
    spec = load(spec_path)

    facts = validated.get("facts", [])

    requirements = [
        fact
        for fact in facts
        if fact.get("fact_type") in {
            "requirement",
            "scoring",
            "submission",
            "technology",
            "timeline",
        }
    ]

    selected = spec.get("selected_idea", {})
    product = spec.get("product", {})
    technical_scope = spec.get("technical_scope", {})
    partner_stack = spec.get("partner_stack", {})
    submission = spec.get("submission", {})
    success_criteria = spec.get("success_criteria", [])

    product_name = (
        text(product.get("name"))
        or text(selected.get("name"))
        or "MVP Product"
    )

    product_description = (
        text(product.get("description"))
        or text(selected.get("product"))
        or text(selected.get("problem"))
    )

    mappings = []

    for index, requirement in enumerate(requirements, 1):
        rid = fact_id(requirement, index)
        rule = text(requirement.get("text"))

        if not rule:
            continue

        normalized = rule.lower()

        feature = None
        engineering = None
        verification = None

        if any(
            term in normalized
            for term in (
                "memory",
                "persist",
                "recall",
                "state",
            )
        ):
            feature = "Persistent agent memory"
            engineering = "Implement persistent memory store and recall/load flow"
            verification = "Memory round-trip integration test"

        elif any(
            term in normalized
            for term in (
                "gate",
                "permission",
                "allow",
                "deny",
                "safety",
            )
        ):
            feature = "Deterministic action safety gate"
            engineering = "Route every executable action through the deterministic gate"
            verification = "Allowed, denied, malformed, and gate-routing tests"

        elif any(
            term in normalized
            for term in (
                "base action",
                "transaction",
                "execution",
            )
        ):
            feature = "Safe base action execution"
            engineering = "Implement the base action interface with safe default behavior"
            verification = "Base action end-to-end test"

        elif any(
            term in normalized
            for term in (
                "submission",
                "submit",
                "demo",
            )
        ):
            feature = "Hackathon submission/demo workflow"
            engineering = "Create and verify required submission artifacts"
            verification = "Submission artifact verification"

        elif any(
            term in normalized
            for term in (
                "partner",
                "integration",
                "technology",
                "stack",
            )
        ):
            feature = "Required ecosystem integration"
            engineering = "Implement and test the required partner/technology integration"
            verification = "Integration test against the required dependency"

        elif any(
            term in normalized
            for term in (
                "deadline",
                "timeline",
            )
        ):
            feature = "Deadline and delivery tracking"
            engineering = "Track required delivery milestones"
            verification = "Timeline completeness check"

        elif any(
            term in normalized
            for term in (
                "judge",
                "judging",
                "score",
                "criteria",
            )
        ):
            feature = "Judging-criteria coverage"
            engineering = "Map product capabilities to the judging criteria"
            verification = "Judging-criteria traceability check"

        else:
            feature = "Requirement coverage"
            engineering = "Review and implement requirement-specific product behavior"
            verification = "Requirement-specific verification test"

        mappings.append(
            {
                "requirement_id": rid,
                "requirement": rule,
                "fact_type": requirement.get("fact_type"),
                "source_status": "validated",
                "product_feature": feature,
                "engineering_task": engineering,
                "verification_test": verification,
                "implementation_status": "PLANNED",
            }
        )

    features = sorted(
        {
            mapping["product_feature"]
            for mapping in mappings
            if mapping.get("product_feature")
        }
    )

    engineering_tasks = sorted(
        {
            mapping["engineering_task"]
            for mapping in mappings
            if mapping.get("engineering_task")
        }
    )

    verification_tests = sorted(
        {
            mapping["verification_test"]
            for mapping in mappings
            if mapping.get("verification_test")
        }
    )

    plan = {
        "status": "PRODUCT_PLAN_READY",
        "hackathon": {
            "run_id": validated.get("run_id") or spec.get("run_id"),
        },
        "product": {
            "status": "PLANNED",
            "name": product_name,
            "one_sentence_description": product_description,
            "selected_idea": selected,
            "features": features,
            "integrations": partner_stack,
        },
        "architecture": {
            "status": "PLANNED",
            "memory": spec.get("memory", {}),
            "agent_loop": spec.get("agent_loop", {}),
            "base_action": spec.get("base_action", {}),
            "technical_scope": technical_scope,
        },
        "engineering": {
            "status": "PLANNED",
            "tasks": engineering_tasks,
            "phases": [
                {
                    "phase": 1,
                    "name": "Foundation",
                    "tasks": [
                        "Establish project structure and dependencies",
                        "Implement deterministic safety boundary",
                    ],
                },
                {
                    "phase": 2,
                    "name": "Core Product",
                    "tasks": [
                        "Implement the selected MVP behavior",
                        "Implement persistent state/memory where required",
                    ],
                },
                {
                    "phase": 3,
                    "name": "Integrations",
                    "tasks": [
                        "Implement required partner and technology integrations",
                    ],
                },
                {
                    "phase": 4,
                    "name": "Verification",
                    "tasks": verification_tests,
                },
                {
                    "phase": 5,
                    "name": "Submission",
                    "tasks": [
                        "Validate submission requirements",
                        "Validate demo flow",
                        "Validate judging-criteria coverage",
                    ],
                },
            ],
        },
        "traceability": {
            "status": "READY",
            "rules_to_product_to_engineering": mappings,
        },
        "constraints": {
            "must_verify": [
                "eligibility",
                "required_technologies",
                "required_integrations",
                "submission_requirements",
                "deployment_requirements",
                "restrictions",
                "judging_criteria",
            ],
            "unknowns_must_be_marked": True,
            "fabricated_evidence_forbidden": True,
        },
        "verification": {
            "status": "PLANNED",
            "product_tests": verification_tests,
            "requirement_tests": verification_tests,
            "integration_tests": [],
            "submission_checks": submission,
            "success_criteria": success_criteria,
            "gaps": [],
        },
    }

    output = records / "product_plan.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print("PRODUCT PLAN CREATED")
    print(f"Requirements mapped: {len(mappings)}")
    print(f"Product features: {len(features)}")
    print(f"Engineering tasks: {len(engineering_tasks)}")
    print(f"Verification tests: {len(verification_tests)}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
