#!/usr/bin/env python3

import json
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse


INPUT_FILE = "research/hackathon/raw/latest.json"
OUTPUT_FILE = "research/hackathon/records/latest.json"


def load_source():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_record(source):
    parsed_url = urlparse(source["final_url"])

    record = {
        "research_type": "hackathon",
        "status": "RESEARCHED",
        "researched_at": datetime.now(timezone.utc).isoformat(),

        "source": {
            "submitted_url": source["source_url"],
            "final_url": source["final_url"],
            "domain": parsed_url.netloc,
            "title": source["title"],
        },

        "hackathon": {
            "name": source["title"],
            "organizer": None,
            "deadline": None,
            "start_date": None,
            "end_date": None,
            "eligibility": [],
            "tracks": [],
            "required_technologies": [],
            "required_integrations": [],
            "prizes": [],
            "judging_criteria": [],
            "submission_requirements": [],
            "deployment_requirements": [],
            "restrictions": []
        },

        "evidence": [],

        "discovered_links": source["links"],

        "research_notes": [
            "Initial page fetched successfully.",
            "Hackathon facts require extraction from page content and linked official sources."
        ]
    }

    return record


def main():
    source = load_source()
    record = build_record(source)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(record, file, indent=2, ensure_ascii=False)

    print("HACKATHON RESEARCH RECORD CREATED")
    print(f"Name: {record['hackathon']['name']}")
    print(f"Domain: {record['source']['domain']}")
    print(f"Discovered links: {len(record['discovered_links'])}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
