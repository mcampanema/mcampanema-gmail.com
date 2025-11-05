# SuperBeing Multi-Agent Obsidian Vault

This vault serves as the **central nervous system** for the SuperBeing multi-agent stack.

## Architecture

```
           User
             │
             ▼
        tickets/inbox/  ← Drop tickets here
             │
             ▼
     Claude Web (PM/Orchestrator)
      - Reads tickets
      - Decomposes into subtasks
      - Delegates to specialists
      - Monitors progress
      - Synthesizes results
             │
    ┌────────┼────────┬───────┐
    ▼        ▼        ▼       ▼
  Gemini  CCskills  Codex  Llama
  (cheap)  (smart)  (code) (free)
    │        │        │       │
    └────────┴────────┴───────┘
             │
             ▼
      artifacts/  ← Final outputs
```

## Folder Structure

### `/tickets/` - Task Intake
- **inbox/** - New tickets from user
- **active/** - Being processed by orchestrator
- **done/** - Completed tickets

### `/tasks/` - Agent Work Assignments
- **delegated/{agent}/** - Pending tasks for each agent
- **active/** - Tasks currently being worked
- **done/** - Completed subtasks

### `/notes/` - Agent Research & Findings
- **{agent}/** - Each agent's working notes
- **orchestrator/** - Coordination notes

### `/decisions/` - Architecture Decision Records
- ADRs documenting key decisions with rationale
- Format: `ADR-001-decision-title.md`

### `/artifacts/` - Final Deliverables
- **code/** - Implemented features
- **reports/** - Analysis documents
- **diagrams/** - Visualizations

### `/context/` - Shared Codebase Knowledge
- **architecture/** - System design docs
- **patterns/** - Common patterns used
- **gotchas/** - Known issues and workarounds

### `/daily/` - Daily Logs
- Daily notes per agent: `YYYY-MM-DD/{agent}.md`

### `/templates/` - Note Templates
- Standardized formats for consistency

## Coordination Protocol

### 1. Ticket Creation (User)

Create ticket in `/tickets/inbox/`:

```markdown
---
id: ticket-001
priority: high
type: feature
status: pending
assigned: null
---

# Add Dark Mode Toggle

## Description
Users want dark mode for the video player interface.

## Acceptance Criteria
- [ ] Toggle button in UI
- [ ] Persists preference in localStorage
- [ ] Smooth transition animation
```

### 2. Orchestrator (Claude Web) Processes

1. Moves ticket to `/tickets/active/`
2. Creates task breakdown in `/tasks/`
3. Delegates subtasks to `/tasks/delegated/{agent}/`
4. Creates tracking note in `/notes/orchestrator/`

### 3. Executive Agents Work

Each agent:
1. Polls `/tasks/delegated/{agent}/`
2. Picks up task
3. Moves to `/tasks/active/`
4. Works on task, writes notes to `/notes/{agent}/`
5. Updates task status
6. Moves to `/tasks/done/` when complete

### 4. Orchestrator Synthesizes

1. Monitors `/tasks/done/`
2. Reviews agent notes
3. Synthesizes final artifact
4. Saves to `/artifacts/`
5. Updates ticket status
6. Moves ticket to `/tickets/done/`

## Agent Specializations

### Gemini Flash
- **Role**: Quick analysis, summaries, cheap research
- **Use for**: Code reviews, documentation, simple Q&A
- **Cost**: $$$

### CCskills (Claude CLI)
- **Role**: Deep reasoning, complex problems
- **Use for**: Architecture decisions, refactoring, security
- **Cost**: $$$$$

### Codex (OpenAI)
- **Role**: Code generation, implementation
- **Use for**: Writing functions, boilerplate, tests
- **Cost**: $$$$

### Llama (Local)
- **Role**: Free-tier fallback, simple tasks
- **Use for**: Code formatting, basic Q&A, validation
- **Cost**: FREE!

## Tags System

Use tags to organize and track:

- `#status/pending` `#status/active` `#status/done` `#status/blocked`
- `#agent/gemini` `#agent/ccskills` `#agent/codex` `#agent/llama`
- `#priority/high` `#priority/medium` `#priority/low`
- `#type/feature` `#type/bug` `#type/refactor` `#type/docs`
- `#needs/review` `#needs/testing` `#needs/deployment`

## Preventing Deep Dives

### Rule: Stay Scoped

Each task note includes:
- **Scope**: Clear boundaries
- **Time Limit**: Max time to spend
- **Exit Criteria**: When to stop and ask orchestrator

Example:

```markdown
## Scope
Analyze VideoPlayer.tsx for performance bottlenecks.
DO NOT refactor code. DO NOT implement fixes.
ONLY identify issues.

## Time Limit
30 minutes max

## Exit Criteria
- List of bottlenecks identified
- Performance metrics collected
- Recommendations documented
```

### Escalation Protocol

If agent needs to go deeper:
1. Create note in `/notes/{agent}/escalation-{topic}.md`
2. Tag with `#needs/orchestrator-review`
3. Wait for orchestrator decision
4. Orchestrator creates new task if approved

## Best Practices

1. **Link Everything** - Use `[[wikilinks]]` liberally
2. **Tag Consistently** - Enables filtering and queries
3. **Update Status** - Keep task notes current
4. **Document Decisions** - Use ADRs for important choices
5. **Cross-Reference** - Link related tickets, tasks, notes
6. **Daily Summaries** - Each agent writes daily note

## Example Workflow

See `examples/workflow-add-dark-mode.md` for a complete example.

## Questions?

Orchestrator (Claude Web) maintains `/notes/orchestrator/coordination-log.md` with decisions and clarifications.
