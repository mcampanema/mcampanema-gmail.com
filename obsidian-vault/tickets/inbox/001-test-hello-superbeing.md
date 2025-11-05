---
id: 001-test-hello-superbeing
created: 2025-01-05 21:00:00
priority: high
type: test
status: pending
assigned: null
estimated_cost: $0.05
actual_cost: $0.00
agents_used: []
---

# Test SuperBeing Multi-Agent System

## Description

Test that all agents can communicate and work together properly.

This is a simple "hello world" to verify:
- Agents can pick up tasks
- Agents can write to Obsidian vault
- Orchestrator can synthesize results
- Everything is working end-to-end

## Acceptance Criteria

- [ ] Gemini agent responds with introduction
- [ ] Codex agent responds with introduction
- [ ] Llama agent responds with introduction
- [ ] Each explains their specialty in plain English
- [ ] Each gives one practical example of how they can help
- [ ] All responses are friendly and encouraging

## Constraints

**Time Limit:** 15 minutes total (5 min per agent)
**Budget Limit:** $0.05
**Output Format:** Friendly markdown report

## Task Breakdown (for Orchestrator)

Suggested decomposition:

**Task 1:** Llama introduction (free)
- Introduce yourself
- Explain you run locally (free!)
- Give one example: "I can help with system diagnostics, file organization, basic testing"

**Task 2:** Gemini introduction ($0.02)
- Introduce yourself
- Explain your specialty (fast research, summaries)
- Give one example: "I can research patents, explain scientific concepts, create study guides"

**Task 3:** Codex introduction ($0.03)
- Introduce yourself
- Explain your specialty (code generation)
- Give one example: "I can write simulations, build prototypes, create tools"

## Expected Output

Create: `/artifacts/reports/001-team-introductions.md`

Should feel like meeting your new team! Warm, friendly, encouraging.
