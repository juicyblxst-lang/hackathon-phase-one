#!/usr/bin/env python3

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen


USER_AGENT = "HackathonPhaseOneResearch/1.0"


def source_id(url):
    digest = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()

    return f"source-{digest[:12]}"


def fetch(url):
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urlopen(
        request,
        timeout=30
    ) as response:
        body = response.read()
        final_url = response.geturl()
        content_type = response.headers.get(
            "Content-Type",
            ""
        )

    text = body.decode(
        "utf-8",
        errors="replace"
    )

    return {
        "final_url": final_url,
        "content_type": content_type,
        "text": text
    }


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/collect_sources.py <run_dir>"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    discovery_file = os.path.join(
        run_dir,
        "records",
        "discovered_sources.json"
    )

    output_dir = os.path.join(
        run_dir,
        "sources"
    )

    with open(
        discovery_file,
        "r",
        encoding="utf-8"
    ) as file:
        discovery = json.load(file)

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    fetched = 0
    skipped = 0
    failed = 0

    # High priority first, then medium, then low.
    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    sources = sorted(
        discovery["sources"],
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99
            ),
            item["url"]
        )
    )

    for item in sources:
        url = item["url"]

        sid = source_id(url)

        output_file = os.path.join(
            output_dir,
            f"{sid}.json"
        )

        if os.path.exists(output_file):
            skipped += 1
            print(
                f"{sid} | SKIPPED | already collected"
            )
            continue

        try:
            result = fetch(url)

            record = {
                "source_id": sid,
                "requested_url": url,
                "final_url": result["final_url"],
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "source_categories": [],
                "priority": item["priority"],
                "status": "FETCHED",
                "content_type": result[
                    "content_type"
                ],
                "text": result["text"],
                "error": None
            }

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    record,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            fetched += 1

            print(
                f"{sid} | FETCHED | "
                f"{item['priority'].upper()} | {url}"
            )

        except Exception as error:
            failed += 1

            record = {
                "source_id": sid,
                "requested_url": url,
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "priority": item["priority"],
                "status": "FAILED",
                "error": str(error)
            }

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    record,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"{sid} | FAILED | "
                f"{item['priority'].upper()} | {url}"
            )

    print("")
    print("EVIDENCE COLLECTION COMPLETE")
    print(f"Fetched: {fetched}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    main()
