#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 research/hackathon/verify_product_plan.py RUN_DIR")
        sys.exit(1)

    run_dir = Path(sys.argv[1]).resolve()
    records = run_dir / "records"

    path = records / "product_plan.json"

    if not path.exists():
        print("ERROR: product_plan.json missing.")
        sys.exit(1)

    plan = load(path)

    checks = {
        "product_section": isinstance(plan.get("product"), dict),
        "architecture_section": isinstance(plan.get("architecture"), dict),
        "engineering_section": isinstance(plan.get("engineering"), dict),
        "traceability_section": isinstance(plan.get("traceability"), dict),
        "verification_section": isinstance(plan.get("verification"), dict),
        "unknowns_must_be_marked": (
            plan.get("constraints", {}).get("unknowns_must_be_marked") is True
        ),
        "fabricated_evidence_forbidden": (
            plan.get("constraints", {}).get("fabricated_evidence_forbidden") is True
        ),
    }

    mappings = plan.get("traceability", {}).get(
        "rules_to_product_to_engineering",
        [],
    )

    checks["requirement_traceability"] = isinstance(mappings, list)

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "requirement_mappings": len(mappings),
    }

    output = records / "product_plan_verification.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("PRODUCT PLAN VERIFICATION COMPLETE")
    print(f"Status: {result['status']}")
    print(f"Requirement mappings: {len(mappings)}")
    print(f"Saved: {output}")

    if result["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
