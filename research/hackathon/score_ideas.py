#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def score_idea(idea):
    name = idea["name"]

    scores = {
        "memory_load_bearing": 0,
        "innovation": 0,
        "technical_execution": 0,
        "pitch": 0,
        "pmf": 0,
        "partner_multiplier": 1.00,
    }

    if name == "Persistent Research Agent":
        scores.update({
            "memory_load_bearing": 39,
            "innovation": 22,
            "technical_execution": 18,
            "pitch": 15,
            "pmf": 7,
            "partner_multiplier": 1.00,
        })

    elif name == "Persistent Autonomous Commerce Agent":
        scores.update({
            "memory_load_bearing": 38,
            "innovation": 23,
            "technical_execution": 14,
            "pitch": 13,
            "pmf": 8,
            "partner_multiplier": 1.25,
        })

    elif name == "Agent Memory Decision Journal":
        scores.update({
            "memory_load_bearing": 39,
            "innovation": 21,
            "technical_execution": 18,
            "pitch": 14,
            "pmf": 3,
            "partner_multiplier": 1.00,
        })

    elif name == "Persistent Customer Success Agent":
        scores.update({
            "memory_load_bearing": 37,
            "innovation": 19,
            "technical_execution": 17,
            "pitch": 14,
            "pmf": 8,
            "partner_multiplier": 1.00,
        })

    elif name == "Long-Term Personal Operations Agent":
        scores.update({
            "memory_load_bearing": 36,
            "innovation": 18,
            "technical_execution": 15,
            "pitch": 13,
            "pmf": 7,
            "partner_multiplier": 1.00,
        })

    rubric = (
        scores["memory_load_bearing"]
        + scores["innovation"]
        + scores["technical_execution"]
        + scores["pitch"]
    )

    final_score = (rubric + scores["pmf"]) * scores["partner_multiplier"]

    return {
        "idea_id": idea["idea_id"],
        "name": name,
        "rubric_score": rubric,
        "pmf_bonus": scores["pmf"],
        "partner_multiplier": scores["partner_multiplier"],
        "final_score": round(final_score, 2),
        "component_scores": scores,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 research/hackathon/score_ideas.py <run_dir>")
        raise SystemExit(1)

    run_dir = Path(sys.argv[1])
    ideas_path = run_dir / "records" / "ideas.json"
    output_path = run_dir / "records" / "scored_ideas.json"

    with ideas_path.open(encoding="utf-8") as f:
        data = json.load(f)

    scored = [
        score_idea(idea)
        for idea in data.get("ideas", [])
    ]

    scored.sort(
        key=lambda x: x["final_score"],
        reverse=True,
    )

    output = {
        "run_id": data.get("run_id"),
        "status": "SCORED",
        "ideas": scored,
        "recommended_idea": scored[0]["idea_id"] if scored else None,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("IDEA SCORING COMPLETE")
    print("")
    for rank, idea in enumerate(scored, 1):
        print(
            f"{rank}. {idea['idea_id']} | "
            f"{idea['name']} | "
            f"rubric={idea['rubric_score']} | "
            f"pmf=+{idea['pmf_bonus']} | "
            f"multiplier=x{idea['partner_multiplier']:.2f} | "
            f"final={idea['final_score']}"
        )

    print("")
    print(f"Recommended: {output['recommended_idea']}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
