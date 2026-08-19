#!/usr/bin/env python3

import json
import os
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verify_project(run_dir):
    validated_path = os.path.join(
        run_dir,
        "records",
        "validated.json",
    )

    spec_path = os.path.join(
        run_dir,
        "records",
        "mvp_spec.json",
    )

    if not os.path.exists(validated_path):
        print("ERROR: validated.json missing.")
        sys.exit(1)

    if not os.path.exists(spec_path):
        print("ERROR: mvp_spec.json missing.")
        sys.exit(1)

    facts_data = load_json(validated_path)
    spec = load_json(spec_path)

    facts = facts_data.get("facts", [])
    selected = spec.get("selected_idea", {})

    checks = []

    checks.append({
        "check": "validated_research_present",
        "status": "PASS" if facts else "FAIL",
        "evidence": f"{len(facts)} validated facts",
    })

    checks.append({
        "check": "selected_product_present",
        "status": "PASS" if selected else "FAIL",
        "evidence": selected.get("name", ""),
    })

    required_sections = [
        "product",
        "memory",
        "agent_loop",
        "partner_stack",
        "base_action",
        "technical_scope",
        "submission",
        "demo_story",
        "success_criteria",
    ]

    for section in required_sections:
        value = spec.get(section)

        checks.append({
            "check": f"mvp_spec_{section}",
            "status": "PASS" if value not in (None, "", [], {}) else "FAIL",
            "evidence": f"{section} present",
        })

    passed = sum(
        check["status"] == "PASS"
        for check in checks
    )

    failed = sum(
        check["status"] == "FAIL"
        for check in checks
    )

    result = {
        "status": "PASS" if failed == 0 else "FAIL",
        "verification_version": "v3",
        "product": {
            "idea_id": selected.get("idea_id"),
            "name": selected.get("name"),
        },
        "summary": {
            "validated_facts": len(facts),
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
        },
        "checks": checks,
        "limitations": [
            "This verifies the generated MVP specification structure.",
            "It does not claim that the product has been implemented.",
            "Runtime, deployment, and external integrations require separate execution evidence.",
        ],
    }

    output_path = os.path.join(
        run_dir,
        "records",
        "project_verification.json",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("MVP SPECIFICATION VERIFICATION COMPLETE")
    print()
    print("Product:", selected.get("name"))
    print("Validated facts:", len(facts))
    print("Checks:", len(checks))
    print("Passed:", passed)
    print("Failed:", failed)
    print()
    print("Status:", result["status"])
    print("Saved:", output_path)

    if result["status"] != "PASS":
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/verify_project.py RUN_DIR"
        )
        sys.exit(1)

    verify_project(sys.argv[1])


if __name__ == "__main__":
    main()
