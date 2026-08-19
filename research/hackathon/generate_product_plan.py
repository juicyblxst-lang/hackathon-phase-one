#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def flatten_requirements(value):
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        for key in ("checks", "requirements", "facts", "items"):
            if isinstance(value.get(key), list):
                return value[key]

    return []


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 research/hackathon/generate_product_plan.py RUN_DIR")
        sys.exit(1)

    run_dir = Path(sys.argv[1]).resolve()
    records = run_dir / "records"

    spec_path = records / "hackathon_spec.json"

    if not spec_path.exists():
        print("ERROR: hackathon_spec.json not found.")
        sys.exit(1)

    spec = load(spec_path)

    hackathon = spec.get("hackathon", {})
    requirements = flatten_requirements(spec.get("requirements", {}))

    plan_requirements = []

    for index, requirement in enumerate(requirements, 1):
        if not isinstance(requirement, dict):
            continue

        fact_id = requirement.get("fact_id") or requirement.get("id")
        text = requirement.get("requirement") or requirement.get("text")

        if not text:
            continue

        plan_requirements.append({
            "requirement_id": fact_id or f"requirement-{index:04d}",
            "requirement": text,
            "source_status": (
                "verified"
                if requirement.get("status") == "PASS"
                else "unverified"
            ),
            "product_feature": None,
            "engineering_task": None,
            "verification_test": None,
            "implementation_status": "NOT_IMPLEMENTED",
        })

    plan = {
        "status": "PRODUCT_PLAN_READY",
        "hackathon": {
            "name": hackathon.get("name"),
            "organizer": hackathon.get("organizer"),
            "deadline": hackathon.get("deadline"),
        },

        "product": {
            "status": "PLANNED",
            "name": None,
            "one_sentence_description": None,
            "core_user": None,
            "core_problem": None,
            "core_solution": None,
            "features": [],
            "integrations": [],
        },

        "architecture": {
            "status": "PLANNED",
            "components": [],
            "data_flow": [],
            "security": [],
        },

        "engineering": {
            "status": "PLANNED",
            "phases": [
                {
                    "phase": 1,
                    "name": "Foundation",
                    "tasks": [],
                },
                {
                    "phase": 2,
                    "name": "Core Product",
                    "tasks": [],
                },
                {
                    "phase": 3,
                    "Integrations",
                    "tasks": [],
                },
                {
                    "phase": 4,
                    "Verification",
                    "tasks": [],
                },
                {
                    "phase": 5,
                    "Deployment",
                    "tasks": [],
                },
            ],
        },

        "traceability": {
            "status": "READY",
            "rules_to_product_to_engineering": plan_requirements,
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
            "status": "NOT_RUN",
            "product_tests": [],
            "requirement_tests": [],
            "integration_tests": [],
            "submission_checks": [],
            "gaps": [],
        },
    }

    output = records / "product_plan.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print("PRODUCT PLAN CREATED")
    print(f"Requirements mapped: {len(plan_requirements)}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
