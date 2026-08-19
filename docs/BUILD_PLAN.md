# Persistent Autonomous Procurement Agent — Build Plan

## MVP

One workflow:

> "We need another monitor for the new employee. What should we buy?"

The agent must:
1. Recall persistent procurement policy from Sibyl Memory.
2. Recall relevant previous purchases.
3. Inspect available options.
4. Select an option according to remembered policy.
5. Explain the decision.
6. Execute the Base action.
7. Persist the decision and outcome back to Sibyl Memory.

## Load-bearing memory

Memory stores:
- preferred vendor
- maximum budget
- product restrictions
- approval rules
- previous purchase decisions
- purchase outcomes
- user preferences

### Critical read path

request
→ Sibyl Memory retrieval
→ procurement policy
→ purchase decision
→ action

### Critical write path

policy established
→ Sibyl Memory write

purchase decision
→ Sibyl Memory write

transaction outcome
→ Sibyl Memory write

user correction/exception
→ Sibyl Memory write

## Fresh-session proof

Session A:
1. Establish policy:
   - Dell preferred
   - maximum $400
   - no refurbished equipment
2. Make procurement decision.
3. Persist policy and outcome.

Session B:
1. Start genuinely fresh session.
2. Ask:
   "We need another monitor for the new employee. What should we buy?"
3. Agent recalls policy without prompting.
4. Agent makes a decision using recalled state.
5. Agent executes the Base action.
6. Agent stores the outcome.

## Deletion test

Run the same workflow with Sibyl Memory reads/writes removed.

Expected result:

The agent cannot reliably recover the procurement policy/history and therefore cannot reproduce the demonstrated decision.

If the workflow still works identically, memory is not load-bearing.

## Partner

Required:
- Sibyl Memory

Bonus candidate:
- Base

Do not claim the Base multiplier until a real Base action is successfully exercised in the demo.

Virtuals:
- Out of scope unless it materially improves the core workflow.

## Scope restrictions

Do NOT build:
- general shopping assistant
- multiple commerce categories
- marketplace
- accounting system
- multi-user permissions
- large vendor catalog
- unnecessary UI

## Acceptance criteria

- [ ] Sibyl Memory integration works
- [ ] Policy write works
- [ ] Policy read works
- [ ] Previous purchase retrieval works
- [ ] Memory affects purchase decision
- [ ] Fresh-session recall works
- [ ] Procurement workflow works twice
- [ ] Base action works
- [ ] Outcome is persisted
- [ ] Deletion test fails/degrades correctly
- [ ] README points directly to memory read/write code
- [ ] Demo can show the load-bearing moment in one continuous segment
