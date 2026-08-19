import json
import os
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    return " ".join(str(text).lower().split())


def fact_texts(facts, fact_type=None):
    return [
        fact.get("text", "")
        for fact in facts
        if fact_type is None or fact.get("fact_type") == fact_type
    ]


def contains_any(text, terms):
    text = normalize(text)
    return any(term in text for term in terms)


def verify_project(run_dir):
    facts_data = load_json(
        os.path.join(run_dir, "records", "validated.json")
    )
    ideas_data = load_json(
        os.path.join(run_dir, "records", "ideas.json")
    )

    facts = facts_data.get("facts", [])
    idea = ideas_data["ideas"][0]

    requirements = [
        f for f in facts
        if f.get("fact_type") == "requirement"
    ]

    checks = []

    for req in requirements:
        text = req.get("text", "")
        normalized = normalize(text)

        evidence = []

        # Memory/load-bearing gate
        if contains_any(
            normalized,
            ["memory", "persist", "recall", "load-bearing"]
        ):
            memory = idea.get("memory_role", "")

            if memory:
                status = "PASS"
                evidence.append({
                    "type": "idea",
                    "field": "memory_role",
                    "text": memory,
                })
            else:
                status = "FAIL"

        # Partner-stack requirements
        elif contains_any(
            normalized,
            ["base", "virtuals", "partner stack", "partner"]
        ):
            partner = idea.get("partner_stack", "")

            if partner:
                status = "PASS"
                evidence.append({
                    "type": "idea",
                    "field": "partner_stack",
                    "text": partner,
                })
            else:
                status = "REVIEW"

        # Deployment requirements
        elif "deploy" in normalized:
            status = "REVIEW"
            evidence.append({
                "type": "missing_project_evidence",
                "text": "Deployment evidence is not yet inspected.",
            })

        # Eligibility / legal / participant requirements
        elif contains_any(
            normalized,
            ["18+", "eligibility", "sanctioned", "ip", "intellectual property"]
        ):
            status = "REVIEW"
            evidence.append({
                "type": "manual_review",
                "text": "Participant/submission eligibility requires project-level verification.",
            })

        # Evidence / anti-wrapper requirements
        elif contains_any(
            normalized,
            ["wrapper", "decorative", "fabricated evidence", "real execution"]
        ):
            status = "REVIEW"
            evidence.append({
                "type": "project_inspection_required",
                "text": "Repository/runtime evidence is required to verify actual execution.",
            })

        else:
            status = "REVIEW"

        checks.append({
            "requirement": text,
            "status": status,
            "evidence": evidence,
        })

    passed = sum(c["status"] == "PASS" for c in checks)
    failed = sum(c["status"] == "FAIL" for c in checks)
    review = sum(c["status"] == "REVIEW" for c in checks)

    result = {
        "status": "VERIFIED",
        "verification_version": "v2",
        "idea": {
            "idea_id": idea.get("idea_id"),
            "name": idea.get("name"),
        },
        "summary": {
            "total_requirements": len(checks),
            "passed": passed,
            "failed": failed,
            "review": review,
        },
        "checks": checks,
        "limitations": [
            "Repository implementation is not inspected yet.",
            "Runtime execution is not inspected yet.",
            "Deployment is not independently verified yet.",
            "Submission artifacts are not independently verified yet.",
        ],
        "next_verification_layer": [
            "repository evidence",
            "dependency and integration inspection",
            "runtime execution evidence",
            "deployment verification",
            "submission artifact verification",
        ],
    }

    output_path = os.path.join(
        run_dir,
        "records",
        "project_verification.json",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("PROJECT VERIFICATION COMPLETE")
    print()
    print("Idea:", idea.get("name"))
    print("Requirements:", len(checks))
    print("Passed:", passed)
    print("Failed:", failed)
    print("Review:", review)
    print()
    print("Saved:", output_path)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/verify_project.py RUN_DIR"
        )
        sys.exit(1)

    verify_project(sys.argv[1])


if __name__ == "__main__":
    main()
