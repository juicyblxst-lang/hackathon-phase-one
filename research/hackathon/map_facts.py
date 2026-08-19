#!/usr/bin/env python3

import json
import os
import re
import sys


NOISE_PATTERNS = [
    r"^skip to content",
    r"^start dashboard",
    r"^home scoring submissions",
    r"^on this page",
    r"^read more$",
    r"^learn more$",
    r"^menu$",
    r"^navigation$",
    r"^register your team$",
]


def is_noise(text):
    normalized = text.strip().lower()

    for pattern in NOISE_PATTERNS:
        if re.search(pattern, normalized):
            return True

    return False


def normalize(text):
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def confidence(priority, claim_type):
    if priority == "high":
        if claim_type in {
            "requirement",
            "scoring",
            "submission",
            "timeline"
        }:
            return "high"

        return "medium"

    if priority == "medium":
        return "medium"

    return "low"


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/map_facts.py <run_dir>"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    input_file = os.path.join(
        run_dir,
        "claims",
        "latest.json"
    )

    output_file = os.path.join(
        run_dir,
        "records",
        "validated.json"
    )

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    facts = []
    seen = set()

    for claim in data.get("claims", []):
        text = normalize(
            claim.get("text", "")
        )

        if not text:
            continue

        if is_noise(text):
            continue

        # Deduplicate exact normalized statements.
        key = text.lower()

        if key in seen:
            continue

        seen.add(key)

        facts.append({
            "fact_id": f"fact-{len(facts) + 1:04d}",
            "claim_id": claim["claim_id"],
            "source_id": claim["source_id"],
            "source_url": claim["source_url"],
            "priority": claim["priority"],
            "fact_type": claim["claim_type"],
            "confidence": confidence(
                claim["priority"],
                claim["claim_type"]
            ),
            "text": text
        })

    # Highest-confidence research first.
    confidence_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    facts.sort(
        key=lambda fact: (
            confidence_order[fact["confidence"]],
            fact["fact_type"],
            fact["fact_id"]
        )
    )

    # Re-number after sorting.
    for index, fact in enumerate(
        facts,
        start=1
    ):
        fact["fact_id"] = f"fact-{index:04d}"

    result = {
        "run_id": os.path.basename(run_dir),
        "status": "VALIDATED",
        "source_claim_count": len(
            data.get("claims", [])
        ),
        "validated_fact_count": len(facts),
        "facts": facts
    }

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )

    counts = {}

    for fact in facts:
        fact_type = fact["fact_type"]
        counts[fact_type] = (
            counts.get(fact_type, 0) + 1
        )

    print("HACKATHON FACT MAPPING COMPLETE")
    print(
        f"Source claims: "
        f"{len(data.get('claims', []))}"
    )
    print(
        f"Validated facts: {len(facts)}"
    )

    for fact_type in sorted(counts):
        print(
            f"{fact_type}: {counts[fact_type]}"
        )

    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
