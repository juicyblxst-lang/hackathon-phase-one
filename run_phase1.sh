#!/bin/bash
set -e

HACKATHON_URL="$1"
RUN_DIR="runs/hack-sibyllabs-org-56a790a8"

if [ -z "$HACKATHON_URL" ]; then
  echo "Usage: ./run_phase1.sh <hackathon-url>"
  exit 1
fi

echo "========================================"
echo "PHASE 1 — FULL AUTOMATED RUN"
echo "========================================"

echo ""
echo "STEP 1 — INTAKE"
./workflows/intake.sh "$HACKATHON_URL"

echo ""
echo "STEP 2 — FETCH"
python3 research/hackathon/fetch.py "$HACKATHON_URL"

echo ""
echo "STEP 3 — BUILD RECORD"
python3 research/hackathon/build_record.py

echo ""
echo "STEP 4 — DISCOVER SOURCES"
python3 research/hackathon/discover_sources.py "$RUN_DIR"

echo ""
echo "STEP 5 — COLLECT EVIDENCE"
python3 research/hackathon/collect_sources.py "$RUN_DIR"

echo ""
echo "STEP 6 — CLEAN DOCUMENTS"
python3 research/hackathon/clean_sources.py "$RUN_DIR"

echo ""
echo "STEP 7 — EXTRACT CLAIMS"
python3 research/hackathon/extract_claims.py "$RUN_DIR"

echo ""
echo "STEP 8 — MAP FACTS"
python3 research/hackathon/map_facts.py "$RUN_DIR"

echo ""
echo "STEP 9 — VERIFY IDEA"
python3 research/hackathon/verify_idea.py "$RUN_DIR"

echo ""
echo "STEP 10 — VERIFY PROJECT"
python3 research/hackathon/verify_project.py "$RUN_DIR"

echo ""
echo "STEP 11 — VERIFY REPOSITORY"
python3 research/hackathon/verify_repo.py "$RUN_DIR" .

echo ""
echo "STEP 12 — CLASSIFY EVIDENCE"
python3 research/hackathon/classify_evidence.py \
  "$RUN_DIR/records/repo_verification.json"

echo ""
echo "STEP 13 — VERIFY REQUIREMENTS"
python3 research/hackathon/verify_requirements.py "$RUN_DIR"

echo ""
echo "========================================"
echo "PHASE 1 — AUTOMATED RUN COMPLETE"
echo "========================================"

python3 - <<'PY'
import json

p = "runs/hack-sibyllabs-org-56a790a8/records/requirement_verification.json"

with open(p, encoding="utf-8") as f:
    d = json.load(f)

checks = d.get("checks", [])
passed = sum(x.get("status") == "PASS" for x in checks)
failed = sum(x.get("status") == "FAIL" for x in checks)
review = sum(x.get("status") == "REVIEW" for x in checks)

print()
print("FINAL VERDICT")
print("==============")
print("Requirements:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print("Review:", review)

if failed:
    print("VERDICT: FAIL")
elif review:
    print("VERDICT: REVIEW")
else:
    print("VERDICT: PASS")
PY
