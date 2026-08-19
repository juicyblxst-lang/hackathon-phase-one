import json
import os
import re


TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".md", ".txt", ".yaml", ".yml",
    ".toml", ".ini", ".env.example"
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
}


def iter_project_files(project_dir):
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS
            and d != "runs"
        ]

        for filename in files:
            path = os.path.join(root, filename)

            if os.path.splitext(filename)[1].lower() in TEXT_EXTENSIONS:
                yield path


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def search_project(project_dir, patterns):
    evidence = []

    compiled = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in patterns
    ]

    for path in iter_project_files(project_dir):
        text = read_text(path)

        if not text:
            continue

        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):
            for pattern in compiled:
                if pattern.search(line):
                    evidence.append({
                        "file": os.path.relpath(path, project_dir),
                        "line": line_number,
                        "text": line.strip(),
                        "pattern": pattern.pattern,
                    })

    return evidence


def inspect_project(project_dir):
    memory_evidence = search_project(
        project_dir,
        [
            r"sibyl",
            r"memory",
            r"persist",
            r"recall",
            r"retrieve",
        ],
    )

    base_evidence = search_project(
        project_dir,
        [
            r"\bbase\b",
            r"base\.org",
            r"onchain",
            r"transaction",
            r"wallet",
        ],
    )

    runtime_test_evidence = search_project(
        project_dir,
        [
            r"pytest",
            r"unittest",
            r"assert ",
            r"test_",
            r"subprocess",
            r"execute",
            r"runtime",
        ],
    )

    agent_safety_evidence = search_project(
        project_dir,
        [
            r"deterministic gate",
            r"class DeterministicGate",
            r"def check\(",
            r"guarded_execute",
            r"allowed_actions",
        ],
    )

    gate_test_evidence = search_project(
        project_dir,
        [
            r"class DeterministicGate",
            r"def guarded_execute",
            r"def test_allowed_action_reaches_executor",
            r"def test_disallowed_action_is_blocked",
            r"def test_malformed_model_output_is_blocked",
            r"def test_non_dict_model_output_is_blocked",
            r"def test_every_action_must_pass_gate",
            r"DETERMINISTIC GATE TESTS PASSED",
        ],
    )

    wrapper_evidence = search_project(
        project_dir,
        [
            r"import\s+sibyl",
            r"from\s+sibyl",
            r"require\(.*sibyl",
        ],
    )

    agent_safety_evidence = search_project(
        project_dir,
        [
            r"deterministic.?gate",
            r"policy.?gate",
            r"action.?gate",
            r"allow.*deny",
            r"deny.*action",
            r"validate.*action",
            r"validate.*tool",
            r"authorize.*action",
            r"authorize.*tool",
            r"policy.*check",
            r"model.*action",
            r"action.*executor",
            r"before.*execute",
        ],
    )

    return {
        "project_dir": os.path.abspath(project_dir),
        "memory": {
            "matches": memory_evidence,
            "match_count": len(memory_evidence),
        },
        "base": {
            "matches": base_evidence,
            "match_count": len(base_evidence),
        },
        "integration_signals": {
            "matches": wrapper_evidence,
            "match_count": len(wrapper_evidence),
        },
        "agent_safety": {
            "matches": agent_safety_evidence,
            "match_count": len(agent_safety_evidence),
        },
        "runtime_tests": {
            "matches": runtime_test_evidence,
            "match_count": len(runtime_test_evidence),
        },
        "agent_safety": {
            "matches": agent_safety_evidence,
            "match_count": len(agent_safety_evidence),
        },
        "agent_safety_tests": {
            "matches": gate_test_evidence,
            "match_count": len(gate_test_evidence),
        },
    }


def main():
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/evidence_engine.py PROJECT_DIR"
        )
        raise SystemExit(1)

    project_dir = sys.argv[1]

    result = inspect_project(project_dir)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
