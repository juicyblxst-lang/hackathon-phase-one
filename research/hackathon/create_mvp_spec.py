#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 research/hackathon/create_mvp_spec.py <run_dir>")
        raise SystemExit(1)

    run_dir = Path(sys.argv[1])
    output = run_dir / "records" / "mvp_spec.json"

    spec = {
        "run_id": run_dir.name,
        "status": "MVP_SPEC_LOCKED",

        "selected_idea": {
            "idea_id": "idea-005",
            "name": "Persistent Autonomous Procurement Agent",
            "decision": "BUILD",
            "fallback": "idea-001",
            "reason": (
                "Highest modeled hackathon score when the verified partner "
                "multiplier is exercised through the actual product workflow."
            ),
        },

        "product": {
            "one_liner": (
                "An autonomous procurement agent that remembers purchasing "
                "policies and history, uses that memory to make repeat "
                "procurement decisions, and executes the resulting transaction."
            ),

            "target_user": (
                "A small-team operator responsible for recurring equipment "
                "or operational purchases."
            ),

            "pain": (
                "Repeated purchasing requires remembering vendor preferences, "
                "budgets, restrictions, prior decisions, and approval history."
            ),

            "core_workflow": (
                "Purchase a monitor for a new employee while respecting the "
                "company's persistent procurement policy."
            ),
        },

        "memory": {
            "provider": "Sibyl Memory",
            "load_bearing": True,

            "stored_state": [
                "preferred_vendor",
                "maximum_budget",
                "product_restrictions",
                "approval_rules",
                "previous_purchase_decisions",
                "purchase_outcomes",
                "user_preferences",
            ],

            "writes": [
                "Store procurement policy when the user establishes it.",
                "Store each procurement decision before or during execution.",
                "Store transaction outcome after execution.",
                "Store exceptions or user corrections.",
            ],

            "reads": [
                "Retrieve procurement policy before making a purchase decision.",
                "Retrieve relevant prior purchases before selecting an item.",
                "Retrieve exceptions before executing the transaction.",
                "Retrieve prior outcomes when evaluating future purchases.",
            ],

            "deletion_test": (
                "Removing Sibyl Memory must cause the agent to lose the "
                "persistent procurement policy and purchase history required "
                "to make the demonstrated decision correctly."
            ),
        },

        "agent_loop": [
            "Receive procurement request.",
            "Recall relevant persistent procurement state.",
            "Search or inspect available purchase options.",
            "Evaluate options against remembered policy.",
            "Explain the selected option.",
            "Execute the transaction/action through Base.",
            "Store the decision and outcome in Sibyl Memory.",
        ],

        "partner_stack": {
            "required": [
                "Sibyl Memory"
            ],
            "verified_bonus": [
                "Base"
            ],
            "optional": [
                "Virtuals"
            ],
            "rule": (
                "Partner integration must perform real product work in the "
                "demo; merely importing a package does not count."
            ),
        },

        "base_action": {
            "purpose": (
                "Execute a real onchain action associated with the procurement "
                "workflow so the Base integration is visibly functional."
            ),
            "requirement": (
                "The exact transaction/action must be implemented and "
                "successfully demonstrated before claiming the partner bonus."
            ),
        },

        "fresh_session_demo": {
            "required": True,
            "sequence": [
                {
                    "step": 1,
                    "action": (
                        "Tell the agent: Dell preferred, maximum $400, "
                        "no refurbished equipment."
                    ),
                },
                {
                    "step": 2,
                    "action": (
                        "Have the agent perform a procurement decision and "
                        "persist the policy and outcome."
                    ),
                },
                {
                    "step": 3,
                    "action": (
                        "Start a genuinely fresh session."
                    ),
                },
                {
                    "step": 4,
                    "action": (
                        "Ask: 'We need another monitor for the new employee. "
                        "What should we buy?'"
                    ),
                },
                {
                    "step": 5,
                    "action": (
                        "Agent recalls the policy without the user repeating it."
                    ),
                },
                {
                    "step": 6,
                    "action": (
                        "Agent makes a decision using the recalled state."
                    ),
                },
                {
                    "step": 7,
                    "action": (
                        "Agent executes the Base action and records the outcome."
                    ),
                },
            ],
        },

        "gate_proof": {
            "cold_start_recall": True,
            "critical_path_calls": True,
            "deletion_test": True,
            "proof_requirements": [
                "Show memory write in repository code.",
                "Show memory read in repository code.",
                "Show fresh-session recall in one continuous demo segment.",
                "Show that removing memory breaks or materially degrades the core workflow.",
            ],
        },

        "technical_scope": {
            "must_build": [
                "Agent runtime",
                "Sibyl Memory integration",
                "Procurement policy memory",
                "Relevant-memory retrieval",
                "Purchase decision logic",
                "Single procurement workflow",
                "Base integration",
                "Transaction/outcome persistence",
                "Minimal web or chat interface",
            ],

            "out_of_scope": [
                "General-purpose shopping assistant",
                "Multiple commerce categories",
                "Production-grade marketplace integration",
                "Complex multi-user permissions",
                "Full accounting system",
                "Large-scale vendor catalog",
                "Unnecessary UI polish",
                "Virtuals integration unless it materially improves the core demo",
            ],
        },

        "submission": {
            "repo": True,
            "license": "MIT or Apache-2.0",
            "demo_duration_minutes": "2-5",
            "fresh_session_recall_required": True,
            "readme_sections": [
                "What it does",
                "Where memory is load-bearing",
                "Memory writes and reads",
                "Base integration",
                "How memory made this possible",
                "Prior Work declaration",
            ],
            "public_posts": [
                "Demo video",
                "At least one build-log",
            ],
        },

        "demo_story": [
            "Problem: recurring procurement requires persistent organizational memory.",
            "Policy is established once.",
            "Agent makes a purchase decision using that policy.",
            "A fresh session begins.",
            "Agent recalls the policy without being reminded.",
            "Agent makes a new decision from persistent state.",
            "Agent executes the real Base action.",
            "Agent persists the new outcome.",
            "Deletion test proves memory is load-bearing.",
        ],

        "success_criteria": [
            "Fresh session recalls procurement policy.",
            "Recall materially changes the agent's decision.",
            "Memory is on the critical path.",
            "Base performs a real action in the product.",
            "The demo works twice consecutively.",
            "A judge can find memory reads/writes in under two minutes.",
            "The product is understandable without explaining the architecture first.",
        ],
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    print("MVP SPEC CREATED")
    print(f"Selected: {spec['selected_idea']['name']}")
    print(f"Status: {spec['status']}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
