#!/usr/bin/env python3

import json
import os
import re
import sys
from html import unescape


def clean_text(text):
    if not text:
        return ""

    # Remove scripts and styles.
    text = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove HTML tags.
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Decode HTML entities.
    text = unescape(text)

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 research/hackathon/clean_sources.py <run_dir>"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    source_dir = os.path.join(
        run_dir,
        "sources"
    )

    clean_dir = os.path.join(
        source_dir,
        "clean"
    )

    os.makedirs(
        clean_dir,
        exist_ok=True
    )

    processed = 0
    skipped = 0

    for filename in sorted(
        os.listdir(source_dir)
    ):
        if not filename.endswith(".json"):
            continue

        input_file = os.path.join(
            source_dir,
            filename
        )

        output_file = os.path.join(
            clean_dir,
            filename
        )

        if os.path.exists(output_file):
            skipped += 1
            continue

        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as file:
            source = json.load(file)

        cleaned = clean_text(
            source.get("text", "")
        )

        record = {
            "source_id": source["source_id"],
            "requested_url": source["requested_url"],
            "final_url": source.get("final_url"),
            "retrieved_at": source.get("retrieved_at"),
            "priority": source.get("priority"),
            "status": "CLEANED",
            "text": cleaned,
            "character_count": len(cleaned)
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

        processed += 1

        print(
            f"{source['source_id']} | CLEANED"
        )

    print("")
    print("DOCUMENT CLEANING COMPLETE")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Saved: {clean_dir}")


if __name__ == "__main__":
    main()
