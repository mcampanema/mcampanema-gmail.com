# SuperBeing Multi-Agent Coordination Protocol

This document defines how agents communicate and coordinate through the Obsidian vault.

## Roles

### Orchestrator (Claude Code Web)
**You are the PM/Coordinator**

**Responsibilities:**
- Process tickets from `/tickets/inbox/`
- Analyze complexity and cost
- Decompose into subtasks
- Delegate to executive agents
- Monitor progress
- Synthesize results
- Create final deliverables

**Location:** Runs in Claude Code Web worker VM

### Executive Agents
**Specialists who execute subtasks**

**Gemini Flash:**
- Quick analysis
- Documentation
- Code reviews
- Summaries
- **Cost:** $ (cheap)

**CCskills (Claude CLI):**
- Complex reasoning
- Architecture decisions
- Security audits
- Refactoring
- **Cost:** $$$ (expensive)

**Codex (OpenAI):**
- Code generation
- Implementation
- Test writing
- **Cost:** $$ (moderate)

**Llama (Local):**
- Fallback for simple tasks
- Code formatting
- Basic Q&A
- **Cost:** FREE!

## Workflow

### Phase 1: Ticket Intake

**User** creates ticket in `/tickets/inbox/`:

```bash
# Option 1: Copy template
cp obsidian-vault/templates/ticket.md obsidian-vault/tickets/inbox/my-ticket.md

# Option 2: Use CLI helper (TODO)
./create-ticket.sh "Add dark mode" --priority high --type feature
```

### Phase 2: Orchestrator Analysis

**Claude Web** runs:

```bash
python3 scripts/orchestrator.py --vault obsidian-vault/
```

This:
1. ✓ Reads ticket from `/tickets/inbox/`
2. ✓ Analyzes complexity (simple, medium, complex)
3. ✓ Estimates cost ($, $$, $$$)
4. ✓ Recommends agents (Llama < Gemini < Codex < CCskills)
5. ⚠ **PAUSES** - Claude Web takes over manually

### Phase 3: Manual Decomposition (YOU = Claude Web)

**You** (Claude in web worker) now:

1. **Read the ticket carefully**
   ```python
   ticket = load_ticket("obsidian-vault/tickets/inbox/001-dark-mode.md")
   print(ticket['body'])
   ```

2. **Decompose into subtasks**
   Think: What specific, bounded tasks are needed?

   Example for "Add dark mode":
   - Task 1: Audit existing CSS (Gemini, 20min)
   - Task 2: Design color scheme (CCskills, 30min)
   - Task 3: Implement toggle component (Codex, 45min)
   - Task 4: Add localStorage persistence (Codex, 20min)
   - Task 5: Test across browsers (Llama, 15min)

3. **Create task notes**
   ```python
   from scripts.orchestrator import create_task_note, move_ticket, create_orchestrator_note

   vault_path = "obsidian-vault"

   tasks = [
       {
           'subtask_id': '001',
           'agent': 'gemini',
           'title': 'Audit existing CSS for theme support',
           'objective': 'Identify which CSS files need dark mode variants',
           'estimated_time': '20min',
           'max_time': '30 minutes',
           'exit_criteria': '- [ ] List of CSS files\n- [ ] Current color palette documented',
           'files': 'index.css\nVideoPlayer.tsx',
           'output_format': 'markdown report',
           'artifact_dir': 'reports',
           'must_include': '- Complete list of CSS files\n- Color variables currently used',
           'agent_instructions': 'Focus ONLY on listing files and colors. Do NOT propose changes.'
       },
       # ... more tasks
   ]

   for task_data in tasks:
       create_task_note(vault_path, ticket, task_data)

   # Move ticket to active
   move_ticket(ticket['path'], vault_path, 'active')

   # Create coordination note
   create_orchestrator_note(vault_path, ticket, analysis, tasks)
   ```

4. **Commit and push**
   ```bash
   cd obsidian-vault
   git add tasks/ tickets/ notes/
   git commit -m "[orchestrator] Decomposed ticket 001-dark-mode into 5 tasks"
   git push
   ```

### Phase 4: Executive Agents Pick Up Tasks

**On local machine** (or wherever agents run), start agent workers:

```bash
# Terminal 1 - Gemini
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent gemini \
  --api-key $GEMINI_API_KEY

# Terminal 2 - Codex
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent codex \
  --api-key $OPENAI_API_KEY

# Terminal 3 - Llama (local)
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent llama

# Terminal 4 - CCskills (only if needed)
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent ccskills \
  --api-key $ANTHROPIC_API_KEY
```

Each agent:
1. Polls `/tasks/delegated/{agent}/` every 30s
2. Picks up first task
3. Moves to `/tasks/active/`
4. Executes task (calls API)
5. Saves artifact to `/artifacts/`
6. Creates note in `/notes/{agent}/`
7. Updates task status to `done`
8. Moves to `/tasks/done/`
9. Commits and pushes

### Phase 5: Orchestrator Monitors Progress

**Claude Web** periodically checks:

```python
# Check task status
import os
from pathlib import Path

vault = Path("obsidian-vault")

pending = len(list((vault / "tasks" / "delegated").rglob("*.md")))
active = len(list((vault / "tasks" / "active").glob("*.md")))
done = len(list((vault / "tasks" / "done").glob("*.md")))

print(f"Pending: {pending}, Active: {active}, Done: {done}")
```

Update coordination note:

```markdown
## Monitoring

**Check Status:** Every 15 minutes
**Tasks Pending:** 2
**Tasks Active:** 1
**Tasks Done:** 2

## Progress Log

### 2024-01-15 14:30:00
- Gemini completed CSS audit
- Codex working on toggle component
- Waiting on CCskills for color scheme
```

### Phase 6: Synthesize Results

When all tasks complete, **Claude Web**:

1. **Review artifacts**
   ```bash
   ls obsidian-vault/artifacts/reports/
   # 001-001-output.md (Gemini CSS audit)
   # 001-002-output.md (CCskills color scheme)
   # ...
   ```

2. **Read agent notes**
   ```bash
   ls obsidian-vault/notes/*/
   ```

3. **Create final deliverable**
   Synthesize into complete solution

4. **Update ticket**
   ```markdown
   ## Status: DONE

   All subtasks completed. Final deliverable: [[dark-mode-implementation.md]]

   **Cost:** $0.45 total
   - Gemini: $0.01
   - CCskills: $0.15
   - Codex: $0.25
   - Llama: $0.00
   ```

5. **Move ticket to done**
   ```bash
   mv obsidian-vault/tickets/active/001-dark-mode.md obsidian-vault/tickets/done/
   ```

6. **Commit final state**
   ```bash
   cd obsidian-vault
   git add .
   git commit -m "[orchestrator] Completed ticket 001-dark-mode"
   git push
   ```

## Communication Patterns

### Escalation (Agent → Orchestrator)

If agent needs to go deeper or is blocked:

```markdown
# /notes/gemini/escalation-001-001.md

---
tags: #needs/orchestrator-review
agent: gemini
task: [[001-001-css-audit]]
---

# Escalation: CSS Audit Needs More Time

I've found 47 CSS files, not just the 3 expected.
Auditing all would take ~2 hours, not 20 minutes.

## Question

Should I:
1. Continue with full audit (2 hours)
2. Sample top 10 files only (30 min)
3. Stop here and let CCskills decide architecture

## Recommendation

Option 2 - sample approach, then CCskills makes call.

## Orchestrator Response

[Claude Web will update this section]
```

**Orchestrator** responds:

```markdown
## Orchestrator Response

DECISION: Option 2 - sample approach

Create new task for CCskills:
- [[001-006-architecture-decision]] - Review sample and decide approach

RATIONALE: Stay within budget. CCskills better suited for architecture.

STATUS: Escalation resolved ✓
```

### Clarification (Orchestrator → User)

If orchestrator needs user input:

```markdown
# /notes/orchestrator/clarification-001.md

---
tags: #needs/user-input
ticket: [[001-dark-mode]]
---

# Clarification Needed: Dark Mode Design

## Question

Should dark mode be:
1. Automatic (system preference)
2. Manual toggle only
3. Both options

## Context

Affects implementation complexity:
- Option 1: Simple, 1 hour
- Option 2: Simple, 1 hour
- Option 3: Complex, 3 hours

## User Response

[User will update this section]
```

### Decision Records

For important choices:

```markdown
# /decisions/ADR-001-use-css-variables.md

---
adr: 001
date: 2024-01-15
status: accepted
decides: [[001-dark-mode]]
---

# ADR-001: Use CSS Variables for Theming

## Decision

Implement dark mode using CSS custom properties (variables).

## Rationale

- Easy to maintain
- No JavaScript required for styling
- Better performance
- Standard approach

## Alternatives Considered

### CSS-in-JS
- Cons: Adds bundle size, runtime overhead

### Separate stylesheets
- Cons: Duplication, harder to maintain

## Consequences

- Must support IE11? NO → CSS vars OK
- Enables future themes (not just dark mode)
```

## Anti-Patterns

### ❌ Deep Dive Without Permission

**BAD:**
Agent spends 4 hours refactoring when task was "audit CSS" (20min).

**GOOD:**
Agent hits time limit, creates escalation note, waits for orchestrator.

### ❌ Scope Creep

**BAD:**
Task: "Add toggle button"
Agent: Implements toggle, localStorage, analytics, dark mode color scheme, mobile responsive, accessibility.

**GOOD:**
Task: "Add toggle button"
Agent: Adds ONLY the toggle button component, nothing else.

### ❌ Working Offline

**BAD:**
Agent completes task but doesn't update status in Obsidian.
Orchestrator doesn't know it's done.

**GOOD:**
Agent updates task status, commits notes, pushes to git regularly.

### ❌ Ignoring Exit Criteria

**BAD:**
Task says "STOP when you have 3 examples" but agent finds 47 examples.

**GOOD:**
Agent stops at 3 examples as specified.

## Best Practices

### ✅ Link Everything

Use `[[wikilinks]]` to create knowledge graph:

```markdown
This relates to [[ADR-003-component-architecture]] and [[ticket-012-accessibility]].
```

### ✅ Tag Consistently

```markdown
#status/blocked #needs/orchestrator-review #priority/high #agent/gemini
```

### ✅ Update Status Promptly

Don't wait until end of day. Update as you go:

```markdown
### 14:23
Started task

### 14:45
Found issue with CSS specificity, investigating

### 15:10
Resolved, writing report

### 15:20
Done, artifact saved
```

### ✅ Document Assumptions

```markdown
## Assumptions

- Users have modern browsers (Chrome 90+, Firefox 88+)
- No IE11 support required
- Dark mode is optional feature, not required for launch
```

### ✅ Provide Cost Estimates

```markdown
**Estimated Cost:** $0.15
**Actual Cost:** $0.18 (slightly over due to clarification needed)
```

## Tools

### Query Obsidian with Dataview

```dataview
TABLE status, agent, priority
FROM "tasks/delegated"
WHERE status = "pending"
SORT priority DESC
```

### CLI Helpers

```bash
# Check overall status
./scripts/status.sh

# Create new ticket
./scripts/create-ticket.sh "Fix bug in video player" --priority high

# Summarize costs
./scripts/cost-report.sh
```

## Troubleshooting

### Agent not picking up tasks

Check:
1. Task file in `/tasks/delegated/{agent}/`?
2. Agent worker running?
3. Git repo synced?

### Orchestrator can't find completed work

Check:
1. Agent pushed to git?
2. Task moved to `/tasks/done/`?
3. Artifact exists in `/artifacts/`?

### Merge conflicts in Obsidian vault

```bash
# Stash local changes
git stash

# Pull latest
git pull

# Reapply changes
git stash pop

# Resolve conflicts manually
```

---

**Remember:** Obsidian is the source of truth. All coordination happens through markdown files in the vault. Git keeps everyone in sync.
