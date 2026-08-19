import json
import os
import sys


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    return " ".join(str(text or "").lower().split())


def contains_any(text, terms):
    text = normalize(text)
    return any(term in text for term in terms)


def classify_requirement(text):
    req = normalize(text)

    if contains_any(req, [
        "memory must be load-bearing",
        "load-bearing",
        "load bearing",
        "fresh-session",
        "fresh session",
        "persisted context",
        "persist context",
    ]):
        return "memory_gate"

    if contains_any(req, [
        "thin wrapper",
        "decorative integration",
        "package import",
        "real execution",
        "disqualifies wrappers",
    ]):
        return "anti_wrapper"

    if contains_any(req, [
        "base",
        "virtuals",
        "partner stack",
        "partner stacks",
    ]):
        return "partner"

    if contains_any(req, [
        "deployment",
        "deployed",
        "deploy",
    ]):
        return "deployment"

    if contains_any(req, [
        "fabricated evidence",
        "evidence",
        "proof",
    ]):
        return "evidence"

    if contains_any(req, [
        "18+",
        "18 +",
        "age",
        "sanctioned jurisdictions",
        "jurisdiction",
    ]):
        return "entrant_eligibility"

    if contains_any(req, [
        "staff",
        "reference builds",
        "reference build",
        "showcase-only",
        "showcase only",
        "prize-ineligible",
        "prize ineligible",
        "cannot win prizes",
    ]):
        return "prize_eligibility"

    if contains_any(req, [
        "ip",
        "intellectual property",
        "keep all ip",
    ]):
        return "legal"

    if contains_any(req, [
        "deterministic gate",
        "rules the agent",
        "every action",
    ]):
        return "agent_safety"

    return "other"


def idea_text(idea):
    fields = [
        "name",
        "problem",
        "product",
        "memory_role",
        "engineering",
        "partner_stack",
    ]

    parts = []

    for field in fields:
        value = idea.get(field, "")

        if isinstance(value, list):
            parts.extend(str(x) for x in value)
        else:
            parts.append(str(value))

    return normalize(" ".join(parts))


def fact_evidence(fact):
    return {
        "type": "hackathon_fact",
        "fact_id": fact.get("fact_id"),
        "claim_id": fact.get("claim_id"),
        "source_id": fact.get("source_id"),
        "source_url": fact.get("source_url"),
        "text": fact.get("text"),
    }


def idea_evidence(idea, field):
    return {
        "type": "idea",
        "field": field,
        "text": idea.get(field, ""),
    }


def verify_memory_gate(requirement, idea):
    memory = normalize(idea.get("memory_role", ""))
    product = normalize(idea.get("product", ""))

    if not memory:
        return (
            "FAIL",
            "The proposed idea does not define a load-bearing memory role.",
            []
        )

    if contains_any(memory, [
        "core state",
        "core function",
        "directly determines",
        "operating context",
        "decisions depend",
        "persistent",
        "without persisted",
        "removing memory",
    ]):
        return (
            "PASS",
            "The idea explicitly makes persistent memory part of the core workflow.",
            [idea_evidence(idea, "memory_role")]
        )

    return (
        "REVIEW",
        "The idea mentions memory, but the load-bearing dependency is not sufficiently explicit.",
        [idea_evidence(idea, "memory_role")]
    )


def verify_anti_wrapper(requirement, idea):
    engineering = normalize(idea.get("engineering", ""))
    product = normalize(idea.get("product", ""))

    substantive_terms = [
        "runtime",
        "workflow",
        "retrieval",
        "execution",
        "automation",
        "integration",
        "decision",
        "interface",
        "orchestration",
        "transaction",
    ]

    matches = [
        term for term in substantive_terms
        if term in engineering or term in product
    ]

    if len(matches) >= 2:
        return (
            "PASS",
            "The proposed build contains substantive product execution rather than only a package import.",
            [
                idea_evidence(idea, "engineering"),
                idea_evidence(idea, "product"),
            ]
        )

    return (
        "REVIEW",
        "The build plan does not yet provide enough evidence to rule out a thin wrapper.",
        [
            idea_evidence(idea, "engineering"),
            idea_evidence(idea, "product"),
        ]
    )


def verify_partner(requirement, idea):
    req = normalize(requirement.get("text", ""))
    partner = normalize(idea.get("partner_stack", ""))

    evidence = [idea_evidence(idea, "partner_stack")]

    if "base" in req:
        if "base" in partner:
            return (
                "PASS",
                "The proposed project explicitly includes Base in its partner stack.",
                evidence
            )

        return (
            "REVIEW",
            "The requirement mentions Base, but the proposed project does not explicitly include it.",
            evidence
        )

    if "virtuals" in req:
        if "virtuals" in partner:
            return (
                "PASS",
                "The proposed project explicitly includes Virtuals.",
                evidence
            )

        return (
            "REVIEW",
            "The requirement mentions Virtuals, but the proposed project does not explicitly include it.",
            evidence
        )

    if "partner" in req:
        if partner:
            return (
                "PASS",
                "The proposed project declares a partner stack.",
                evidence
            )

        return (
            "REVIEW",
            "No partner stack is declared.",
            evidence
        )

    return (
        "REVIEW",
        "Partner requirement requires manual interpretation.",
        evidence
    )


def verify_requirement(requirement, idea, facts):
    text = requirement.get("text", "")
    category = classify_requirement(text)

    if category == "memory_gate":
        status, reason, evidence = verify_memory_gate(
            requirement,
            idea
        )

    elif category == "anti_wrapper":
        status, reason, evidence = verify_anti_wrapper(
            requirement,
            idea
        )

    elif category == "partner":
        status, reason, evidence = verify_partner(
            requirement,
            idea
        )

    elif category == "entrant_eligibility":
        status = "REVIEW"
        reason = (
            "This requirement applies to the entrant, "
            "not the software project, so the checker cannot "
            "verify it from project metadata."
        )
        evidence = [fact_evidence(requirement)]

    elif category == "prize_eligibility":
        status = "REVIEW"
        reason = (
            "This depends on entrant affiliation/status and "
            "cannot be established from the proposed project alone."
        )
        evidence = [fact_evidence(requirement)]

    elif category == "deployment":
        status = "REVIEW"
        reason = (
            "Deployment is a project-state requirement. "
            "The current idea record does not prove deployment."
        )
        evidence = [fact_evidence(requirement)]

    elif category == "evidence":
        status = "REVIEW"
        reason = (
            "The checker must inspect the submitted evidence/artifacts "
            "before confirming this requirement."
        )
        evidence = [fact_evidence(requirement)]

    elif category == "legal":
        status = "REVIEW"
        reason = (
            "This is a submission/legal declaration and cannot be "
            "verified from the project idea alone."
        )
        evidence = [fact_evidence(requirement)]

    elif category == "agent_safety":
        status = "REVIEW"
        reason = (
            "The idea record does not yet contain implementation-level "
            "evidence of deterministic action gating."
        )
        evidence = [fact_evidence(requirement)]

    else:
        status = "REVIEW"
        reason = (
            "The requirement has not yet been assigned a specialized "
            "verification rule."
        )
        evidence = [fact_evidence(requirement)]

    return {
        "requirement": text,
        "category": category,
        "status": status,
        "reason": reason,
        "evidence": evidence,
    }


def verify_idea(data):
    facts = data["facts"]
    idea = data["idea"]

    requirements = [
        fact
        for fact in facts
        if fact.get("fact_type") == "requirement"
    ]

    checks = [
        verify_requirement(
            requirement,
            idea,
            facts
        )
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

    categories = {}

    for check in checks:
        category = check["category"]

        if category not in categories:
            categories[category] = {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "review": 0,
            }

        categories[category]["total"] += 1

        if check["status"] == "PASS":
            categories[category]["pass"] += 1
        elif check["status"] == "FAIL":
            categories[category]["fail"] += 1
        else:
            categories[category]["review"] += 1

    return {
        "status": "VERIFIED",
        "verifier_version": "2.0",
        "idea": {
            "idea_id": idea["idea_id"],
            "name": idea["name"],
        },
        "summary": {
            "total_requirements": len(checks),
            "passed": passed,
            "failed": failed,
            "review": review,
        },
        "categories": categories,
        "checks": checks,
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/verify_idea.py RUN_DIR"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    facts_path = os.path.join(
        run_dir,
        "records",
        "validated.json"
    )

    ideas_path = os.path.join(
        run_dir,
        "records",
        "ideas.json"
    )

    facts_data = load_json(facts_path)
    ideas_data = load_json(ideas_path)

    # The scored ideas are already ordered by score.
    idea = ideas_data["ideas"][0]

    result = verify_idea({
        "facts": facts_data["facts"],
        "idea": idea,
    })

    output_path = os.path.join(
        run_dir,
        "records",
        "verification.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("IDEA VERIFICATION COMPLETE")
    print()
    print("Verifier:", result["verifier_version"])
    print("Idea:", idea["name"])
    print()
    print("SUMMARY")
    print("-------")
    print("Requirements:", result["summary"]["total_requirements"])
    print("Passed:", result["summary"]["passed"])
    print("Failed:", result["summary"]["failed"])
    print("Review:", result["summary"]["review"])
    print()
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
