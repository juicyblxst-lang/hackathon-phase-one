#!/usr/bin/env python3

import json
import os
import re
import sys
from urllib.parse import urlparse


HIGH_PRIORITY_PATTERNS = [
    "rules",
    "rule",
    "submission",
    "submit",
    "requirements",
    "judging",
    "scoring",
    "eligibility",
    "tracks",
    "prizes",
    "docs",
    "documentation"
]


MEDIUM_PRIORITY_PATTERNS = [
    "about",
    "faq",
    "guide",
    "register",
    "project",
    "technology",
    "integration"
]


def normalize_url(url):
    url = url.strip()

    if url.startswith("[") and "](" in url:
        url = url.split("](", 1)[1].rstrip(")")

    parsed = urlparse(url)

    if not parsed.scheme:
        return url

    return parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=parsed.path or "/",
        fragment=""
    ).geturl()


def classify(url, root_url):
    normalized = normalize_url(url)
    root = normalize_url(root_url)

    # The original hackathon page is always highest priority.
    if normalized == root:
        return "high"

    lower = normalized.lower()

    if any(
        re.search(pattern, lower)
        for pattern in HIGH_PRIORITY_PATTERNS
    ):
        return "high"

    if any(
        re.search(pattern, lower)
        for pattern in MEDIUM_PRIORITY_PATTERNS
    ):
        return "medium"

    return "low"


def priority_score(priority):
    return {
        "high": 0,
        "medium": 1,
        "low": 2
    }[priority]


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/discover_sources.py <run_dir>"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    input_file = os.path.join(
        run_dir,
        "raw",
        "latest.json"
    )

    output_file = os.path.join(
        run_dir,
        "records",
        "discovered_sources.json"
    )

    with open(input_file, "r", encoding="utf-8") as file:
        source = json.load(file)

    root_url = normalize_url(
        source["final_url"]
    )

    seen = set()
    discovered = []

    # Always include the root page.
    seen.add(root_url)

    discovered.append({
        "url": root_url,
        "priority": "high"
    })

    for raw_url in source.get("links", []):
        url = normalize_url(raw_url)

        if url in seen:
            continue

        seen.add(url)

        discovered.append({
            "url": url,
            "priority": classify(
                url,
                root_url
            )
        })

    discovered.sort(
        key=lambda item: (
            priority_score(item["priority"]),
            item["url"]
        )
    )

    result = {
        "source_url": root_url,
        "total_links": len(discovered),
        "sources": discovered
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

    high = sum(
        1
        for item in discovered
        if item["priority"] == "high"
    )

    medium = sum(
        1
        for item in discovered
        if item["priority"] == "medium"
    )

    low = sum(
        1
        for item in discovered
        if item["priority"] == "low"
    )

    print("SOURCE DISCOVERY COMPLETE")
    print(f"Total unique sources: {len(discovered)}")
    print(f"High priority: {high}")
    print(f"Medium priority: {medium}")
    print(f"Low priority: {low}")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
