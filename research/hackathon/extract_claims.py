#!/usr/bin/env python3

import json
import os
import re
import sys


def split_sentences(text):
    # Split on sentence boundaries while keeping reasonably useful chunks.
    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        part.strip()
        for part in parts
        if len(part.strip()) >= 25
    ]


def classify_claim(sentence):
    lower = sentence.lower()

    if any(
        word in lower
        for word in [
            "must",
            "required",
            "requirement",
            "eligible",
            "eligibility",
            "disqual",
            "cannot",
            "need to",
            "have to"
        ]
    ):
        return "requirement"

    if any(
        word in lower
        for word in [
            "score",
            "points",
            "%",
            "bonus",
            "multiplier",
            "prize"
        ]
    ):
        return "scoring"

    if any(
        word in lower
        for word in [
            "memory",
            "sibyl",
            "base",
            "virtuals",
            "integration",
            "onchain",
            "wallet",
            "x402",
            "acp"
        ]
    ):
        return "technology"

    if any(
        word in lower
        for word in [
            "submit",
            "submission",
            "github",
            "video",
            "readme",
            "post"
        ]
    ):
        return "submission"

    if any(
        word in lower
        for word in [
            "timeline",
            "registration",
            "build window",
            "judging",
            "deadline"
        ]
    ):
        return "timeline"

    return "general"


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/extract_claims.py <run_dir>"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    clean_dir = os.path.join(
        run_dir,
        "sources",
        "clean"
    )

    output_dir = os.path.join(
        run_dir,
        "claims"
    )

    output_file = os.path.join(
        output_dir,
        "latest.json"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    claims = []
    claim_number = 1

    for filename in sorted(
        os.listdir(clean_dir)
    ):
        if not filename.endswith(".json"):
            continue

        input_file = os.path.join(
            clean_dir,
            filename
        )

        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as file:
            source = json.load(file)

        text = source.get(
            "text",
            ""
        )

        sentences = split_sentences(text)

        for sentence in sentences:
            claims.append({
                "claim_id": f"claim-{claim_number:04d}",
                "source_id": source["source_id"],
                "source_url": source["final_url"],
                "priority": source.get("priority"),
                "claim_type": classify_claim(sentence),
                "text": sentence
            })

            claim_number += 1

    result = {
        "run_id": os.path.basename(run_dir),
        "status": "CLAIMS_EXTRACTED",
        "total_claims": len(claims),
        "claims": claims
    }

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

    for claim in claims:
        claim_type = claim["claim_type"]
        counts[claim_type] = (
            counts.get(claim_type, 0) + 1
        )

    print("CLAIM EXTRACTION COMPLETE")
    print(f"Claims found: {len(claims)}")

    for claim_type in sorted(counts):
        print(
            f"{claim_type}: {counts[claim_type]}"
        )

    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
