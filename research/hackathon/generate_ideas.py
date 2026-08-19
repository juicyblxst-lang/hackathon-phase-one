#!/usr/bin/env python3

import json
import os
import re
import sys
from collections import Counter


def load_facts(run_dir):
    path = os.path.join(
        run_dir,
        "records",
        "validated.json"
    )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_facts(data, fact_type=None):
    facts = data.get("facts", [])

    if fact_type:
        return [
            fact for fact in facts
            if fact.get("fact_type") == fact_type
        ]

    return facts


def find_facts(facts, keywords):
    matches = []

    for fact in facts:
        text = fact.get("text", "").lower()

        if any(keyword.lower() in text for keyword in keywords):
            matches.append(fact)

    return matches


def unique_texts(facts):
    seen = set()
    result = []

    for fact in facts:
        text = fact.get("text", "").strip()

        if text and text not in seen:
            seen.add(text)
            result.append(text)

    return result


def build_idea(
    idea_id,
    name,
    problem,
    product,
    memory_role,
    engineering,
    partner_stack,
    strengths,
    risks,
    evidence
):
    return {
        "idea_id": idea_id,
        "name": name,
        "problem": problem,
        "product": product,
        "memory_role": memory_role,
        "engineering": engineering,
        "partner_stack": partner_stack,
        "strengths": strengths,
        "risks": risks,
        "evidence": evidence,
        "validation_status": "PENDING"
    }


def generate_ideas(data):
    facts = data.get("facts", [])

    requirements = get_facts(
        data,
        "requirement"
    )

    scoring = get_facts(
        data,
        "scoring"
    )

    technology = get_facts(
        data,
        "technology"
    )

    submission = get_facts(
        data,
        "submission"
    )

    requirement_text = unique_texts(requirements)
    scoring_text = unique_texts(scoring)
    technology_text = unique_texts(technology)
    submission_text = unique_texts(submission)

    memory_facts = find_facts(
        facts,
        [
            "memory",
            "recall",
            "persist",
            "context"
        ]
    )

    base_facts = find_facts(
        facts,
        [
            "base",
            "onchain",
            "wallet",
            "payment"
        ]
    )

    virtuals_facts = find_facts(
        facts,
        [
            "virtuals",
            "agent",
            "acp",
            "autonomous"
        ]
    )

    evidence = {
        "memory": unique_texts(memory_facts)[:10],
        "requirements": requirement_text[:15],
        "scoring": scoring_text[:15],
        "technology": technology_text[:15],
        "submission": submission_text[:15],
        "base": unique_texts(base_facts)[:10],
        "virtuals": unique_texts(virtuals_facts)[:10]
    }

    ideas = []

    ideas.append(
        build_idea(
            "idea-001",
            "Persistent Research Agent",
            "Researchers repeatedly lose context between research sessions.",
            "An agent that remembers prior research, sources, conclusions, and unresolved questions, then continues research from previous sessions.",
            "Memory is the core state of the research process. Without persisted research history, the agent cannot continue the user's investigation coherently.",
            "Agent runtime, persistent memory reads/writes, source ingestion, retrieval, session management, and a simple web interface.",
            "Sibyl Memory",
            [
                "Sibyl Memory is naturally central; clear fresh-session recall demonstration; strong utility story."
            ],
            [
                "Must demonstrate that memory is essential rather than decorative.",
                "Research retrieval quality must be good enough for the demo."
            ],
            evidence
        )
    )

    ideas.append(
        build_idea(
            "idea-002",
            "Long-Term Personal Operations Agent",
            "Users repeatedly explain their preferences, routines, decisions, and ongoing tasks to agents.",
            "An agent that maintains a persistent operational memory of the user and uses it to execute recurring workflows.",
            "The agent's decisions depend on accumulated user context, preferences, previous actions, and unresolved tasks.",
            "Agent runtime, persistent memory, task orchestration, structured user state, and optional onchain actions.",
            "Sibyl Memory + optional Base/Virtuals",
            [
                "Strong load-bearing memory case; potentially combines agent autonomy with persistent state."
            ],
            [
                "Broad scope can make the product feel generic.",
                "Needs a narrowly defined workflow to prove usefulness."
            ],
            evidence
        )
    )

    ideas.append(
        build_idea(
            "idea-003",
            "Persistent Customer Success Agent",
            "Customer-facing agents forget previous conversations and repeatedly ask customers for the same information.",
            "An autonomous customer-success agent that remembers customer history, preferences, issues, commitments, and previous resolutions.",
            "Customer history becomes the agent's operating context. Removing memory should materially degrade its ability to resolve recurring issues.",
            "Agent runtime, persistent customer memory, CRM-style state, conversation interface, and workflow automation.",
            "Sibyl Memory",
            [
                "Clear real-world pain point; easy fresh-session demonstration; strong PMF potential."
            ],
            [
                "Needs a convincing customer workflow rather than a generic chatbot.",
                "Must show memory affecting actual decisions."
            ],
            evidence
        )
    )

    ideas.append(
        build_idea(
            "idea-004",
            "Agent Memory Decision Journal",
            "Agents make decisions across multiple sessions but lose the reasoning context behind previous decisions.",
            "A persistent decision-memory layer that allows an agent to remember previous decisions, outcomes, assumptions, and lessons learned.",
            "Memory directly determines future decisions by retrieving previous decisions and outcomes before acting.",
            "Agent runtime, structured memory, retrieval, decision logging, evaluation loop, and optional benchmarking.",
            "Sibyl Memory",
            [
                "Very strong memory narrative; easy to demonstrate improvement across sessions."
            ],
            [
                "Must prove that the memory changes future behavior.",
                "Could become a logging tool if the memory is not genuinely load-bearing."
            ],
            evidence
        )
    )

    ideas.append(
        build_idea(
            "idea-005",
            "Persistent Autonomous Commerce Agent",
            "Autonomous agents need to remember users, transactions, preferences, and previous actions to operate reliably over time.",
            "An agent that remembers customer preferences and transaction history while performing autonomous commerce or payment workflows.",
            "Persistent memory determines what the agent should buy, pay, recommend, or avoid based on previous interactions.",
            "Agent runtime, Sibyl Memory, transaction/payment integration, wallet infrastructure, and optional Base/Virtuals integration.",
            "Sibyl Memory + Base/Virtuals",
            [
                "Potentially combines memory with a partner stack and a concrete transactional workflow."
            ],
            [
                "Financial/action flows increase implementation complexity.",
                "Partner integration must perform real work to count."
            ],
            evidence
        )
    )

    return ideas


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 research/hackathon/generate_ideas.py RUN_DIR"
        )
        sys.exit(1)

    run_dir = sys.argv[1]

    data = load_facts(run_dir)

    ideas = generate_ideas(data)

    output_file = os.path.join(
        run_dir,
        "records",
        "ideas.json"
    )

    result = {
        "run_id": data.get("run_id"),
        "status": "IDEAS_GENERATED",
        "source_fact_count": data.get(
            "validated_fact_count",
            len(data.get("facts", []))
        ),
        "idea_count": len(ideas),
        "ideas": ideas
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

    print("IDEA GENERATION COMPLETE")
    print(f"Validated facts used: {result['source_fact_count']}")
    print(f"Ideas generated: {result['idea_count']}")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
