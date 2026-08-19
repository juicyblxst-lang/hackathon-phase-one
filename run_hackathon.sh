#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


def run(cmd, label):
    print()
    print("=" * 56)
    print(label)
    print("=" * 56)

    result = subprocess.run(cmd, cwd=ROOT)

    if result.returncode != 0:
        print()
        print(f"PIPELINE FAILED: {label}")
        sys.exit(result.returncode)


def main():
    if len(sys.argv) != 2:
        print("Usage: ./run_hackathon.sh <hackathon-url>")
        sys.exit(1)

    url = sys.argv[1].strip()

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print("ERROR: Invalid hackathon URL.")
        sys.exit(1)

    run_dir = RUNS / f"hack-{parsed.netloc.replace('.', '-')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "hackathon_url": url,
        "run_dir": str(run_dir),
        "pipeline_status": "STARTED",
    }

    metadata_path = run_dir / "pipeline.json"

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print()
    print("AUTOMATED HACKATHON PIPELINE")
    print(f"Target: {url}")
    print(f"Run:    {run_dir}")

    # Existing intake/research foundation.
    run(
        ["./workflows/intake.sh", url],
        "STEP 1 — INTAKE",
    )

    run(
        ["python3", "research/hackathon/fetch.py", url],
        "STEP 2 — FETCH",
    )

    run(
        ["python3", "research/hackathon/build_record.py"],
        "STEP 3 — BUILD RESEARCH RECORD",
    )

    # Existing research stages that do not require the old
    # Sibyl-specific final verdict.
    run(
        [
            "python3",
            "research/hackathon/discover_sources.py",
            str(run_dir),
        ],
        "STEP 4 — DISCOVER SOURCES",
    )

    run(
        [
            "python3",
            "research/hackathon/collect_sources.py",
            str(run_dir),
        ],
        "STEP 5 — COLLECT EVIDENCE",
    )

    run(
        [
            "python3",
            "research/hackathon/clean_sources.py",
            str(run_dir),
        ],
        "STEP 6 — CLEAN SOURCES",
    )

    run(
        [
            "python3",
            "research/hackathon/extract_claims.py",
            str(run_dir),
        ],
        "STEP 7 — EXTRACT CLAIMS",
    )

    run(
        [
            "python3",
            "research/hackathon/map_facts.py",
            str(run_dir),
        ],
        "STEP 8 — MAP REQUIREMENTS",
    )

    run(
        [
            "python3",
            "research/hackathon/build_spec.py",
            str(run_dir),
        ],
        "STEP 9 — BUILD HACKATHON SPECIFICATION",
    )

    run(
        [
            "python3",
            "research/hackathon/verify_spec.py",
            str(run_dir),
        ],
        "STEP 10 — VERIFY SPECIFICATION",
    )

    run(
        [
            "python3",
            "research/hackathon/pipeline_status.py",
            str(run_dir),
        ],
        "STEP 11 — PIPELINE STATUS",
    )

    run(
        [
            "python3",
            "research/hackathon/generate_product_plan.py",
            str(run_dir),
        ],
        "STEP 12 — GENERATE PRODUCT PLAN",
    )

    run(
        [
            "python3",
            "research/hackathon/verify_product_plan.py",
            str(run_dir),
        ],
        "STEP 13 — VERIFY PRODUCT PLAN",
    )

    metadata["pipeline_status"] = "RESEARCH_COMPLETE"

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print()
    print("=" * 56)
    print("AUTOMATED RESEARCH PIPELINE COMPLETE")
    print("=" * 56)
    print(f"Run directory: {run_dir}")


if __name__ == "__main__":
    main()
