import json
import sys
from pathlib import Path


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def classify_match(match):
    text = str(match.get("text", "")).lower()
    filename = str(match.get("file", "")).lower()

    if filename.startswith("readme"):
        return "weak"

    if (
        "requirements" in filename
        or "package.json" in filename
        or "pyproject.toml" in filename
    ):
        return "dependency"

    # Executable tests are stronger evidence than generic implementation
    # signals. Check the filename first so test imports/assertions remain tests.
    if any(x in filename for x in ["test", "spec"]):
        return "test"

    if any(
        x in text
        for x in [
            "import ",
            "from ",
            "require(",
            "client(",
            "memory.",
            "memory(",
            "retrieve(",
            "persist(",
            "write(",
            "read(",
        ]
    ):
        return "implementation"

    return "signal"


def iter_matches(category_data):
    """
    Accept both:

      {"matches": [...]}

    and unexpected shapes without crashing.
    """
    if isinstance(category_data, dict):
        matches = category_data.get("matches", [])

        if isinstance(matches, list):
            for match in matches:
                if isinstance(match, dict):
                    yield match

    elif isinstance(category_data, list):
        for match in category_data:
            if isinstance(match, dict):
                yield match


def classify_evidence(data):
    classified = []

    raw = data.get("raw_evidence", {})

    if not isinstance(raw, dict):
        raw = {}

    for category, category_data in raw.items():
        for match in iter_matches(category_data):
            item = dict(match)
            item["category"] = category
            item["strength"] = classify_match(match)
            classified.append(item)

    # Runtime gate results are first-class evidence.
    runtime_tests = raw.get("runtime_tests", {})
    if isinstance(runtime_tests, dict):
        if runtime_tests.get("status") == "PASS":
            classified.append({
                "category": "agent_safety",
                "strength": "test",
                "file": "tests/run_gate_tests.py",
                "line": None,
                "text": runtime_tests.get("stdout", "").strip(),
                "pattern": "runtime_gate_execution",
            })
        elif runtime_tests.get("status") in {"FAIL", "TIMEOUT"}:
            classified.append({
                "category": "agent_safety",
                "strength": "signal",
                "file": "tests/run_gate_tests.py",
                "line": None,
                "text": runtime_tests.get("stderr", "").strip(),
                "pattern": "runtime_gate_execution",
            })

    counts = {}

    for item in classified:
        strength = item["strength"]
        counts[strength] = counts.get(strength, 0) + 1

    return {
        "status": "CLASSIFIED",
        "evidence_count": len(classified),
        "strength_counts": counts,
        "evidence": classified,
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/classify_evidence.py "
            "REPO_VERIFICATION_JSON"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    data = load_json(input_path)
    result = classify_evidence(data)

    run_dir = Path(input_path).resolve().parent.parent
    output_path = run_dir / "records" / "evidence_classification.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("EVIDENCE CLASSIFICATION COMPLETE")
    print()
    print("Evidence:", result["evidence_count"])
    print("Strengths:", result["strength_counts"])
    print()
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
