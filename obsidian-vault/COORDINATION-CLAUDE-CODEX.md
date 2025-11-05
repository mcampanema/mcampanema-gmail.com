# 🤝 Coordination Protocol: Claude Web ↔ Codex (VS Code)

**Date:** 2025-01-05
**Status:** ACTIVE

---

## 🎯 Goal

Prevent conflicts while both agents work on the same repository:
- **Claude Code Web** = Orchestrator/PM (me!)
- **Codex in VS Code** = Executive agent (code implementation)
- **Obsidian Vault** = Shared communication channel

---

## 📋 Role Assignment

### Claude Code Web (Orchestrator)
**Responsibilities:**
- Analyze tickets
- Break down into tasks
- Assign tasks to Codex
- Monitor progress
- Synthesize final deliverables
- **DON'T WRITE CODE** (delegate to Codex!)

**Works in:**
- `obsidian-vault/tickets/`
- `obsidian-vault/tasks/`
- `obsidian-vault/notes/orchestrator/`

### Codex in VS Code (Executive Agent)
**Responsibilities:**
- Pick up tasks from `/tasks/delegated/codex/`
- Write code, implement features
- Update task status
- Create agent notes
- Commit code changes

**Works in:**
- Source code files (`.ts`, `.tsx`, `.js`, etc.)
- `obsidian-vault/tasks/delegated/codex/`
- `obsidian-vault/notes/codex/`
- `obsidian-vault/artifacts/code/`

---

## 🌿 Branch Strategy (CRITICAL - Prevents Conflicts!)

### Rule: Each Agent Uses Their Own Branch

**Claude Web Branch:**
```
claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp
```
- Only Claude Web commits here
- Vault coordination, task creation, orchestration

**Codex Branch:**
```
codex/implementation-<date>
```
- Only Codex commits here
- Code changes, implementations

**Merging:**
- User reviews both branches
- User merges when ready
- Or create PR for each

---

## 📁 File Ownership (Who Touches What)

### Claude Web ONLY
- `obsidian-vault/tickets/`
- `obsidian-vault/tasks/` (creates tasks)
- `obsidian-vault/notes/orchestrator/`
- Documentation files

### Codex ONLY
- Source code (`.ts`, `.tsx`, `.js`, `.py`)
- `obsidian-vault/tasks/delegated/codex/` (updates status)
- `obsidian-vault/notes/codex/`
- `obsidian-vault/artifacts/code/`

### Both (Coordinate via Git)
- `obsidian-vault/decisions/` (create ADRs for big decisions)

---

## 🔄 Workflow

### Step 1: User Creates Ticket
```
obsidian-vault/tickets/inbox/002-my-task.md
```

### Step 2: Claude Web Analyzes
- Read ticket
- Decompose into tasks
- Create task notes in `/tasks/delegated/codex/`
- Commit to `claude/` branch
- Push

### Step 3: Codex Picks Up Task

**In VS Code, Codex runs:**
```bash
# Fetch latest from Claude's branch
git fetch origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp

# Merge ONLY the vault (not code changes)
git checkout obsidian-vault/
git merge origin/claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp -- obsidian-vault/

# Check for new tasks
ls obsidian-vault/tasks/delegated/codex/
```

**Or simpler: Just pull the vault folder**
```bash
git pull origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp -- obsidian-vault/tasks/
```

### Step 4: Codex Works on Task

**Codex:**
1. Reads task from `/tasks/delegated/codex/002-my-task-001.md`
2. Moves to `/tasks/active/`
3. Implements the code
4. Saves code to `/artifacts/code/`
5. Creates note in `/notes/codex/`
6. Updates task status to "done"
7. Moves to `/tasks/done/`
8. **Commits to `codex/implementation-<date>` branch**
9. Pushes

### Step 5: Claude Web Sees Completion

**I check:**
```bash
git fetch origin codex/implementation-<date>
git merge origin/codex/implementation-<date> -- obsidian-vault/
```

**Or simpler:**
```bash
git pull origin codex/implementation-<date> -- obsidian-vault/artifacts/ obsidian-vault/notes/codex/ obsidian-vault/tasks/
```

### Step 6: Claude Web Synthesizes
- Review Codex's work
- Create final deliverable
- Update ticket status
- Move to done

---

## 🛡️ Conflict Prevention Rules

### Rule 1: Separate Branches
- **NEVER** work on the same branch simultaneously
- Claude uses `claude/` branches
- Codex uses `codex/` branches

### Rule 2: Communicate via Vault
- Don't edit each other's files directly
- Use `/notes/` to communicate
- Tag with `#needs/codex` or `#needs/orchestrator`

### Rule 3: Pull Before Working
**Codex always:**
```bash
git pull origin claude/... -- obsidian-vault/tasks/
```

**Claude always:**
```bash
git pull origin codex/... -- obsidian-vault/artifacts/ obsidian-vault/notes/codex/
```

### Rule 4: Clear Handoffs
When done with a task, create handoff note:

**Example (Codex → Claude):**
```markdown
# /notes/codex/handoff-002.md

Task 002-001 complete!

**What I did:**
- Implemented VideoPlayer optimization
- Added memoization (lines 45-67)
- Code in /artifacts/code/VideoPlayer.tsx

**For Orchestrator:**
- Please review and test
- Ready to merge into main codebase
- See /notes/codex/002-001.md for details

#needs/orchestrator-review
```

---

## 💬 Communication Examples

### Codex Needs Clarification

**File:** `/notes/codex/question-002.md`
```markdown
---
tags: #needs/orchestrator-review
task: [[002-video-optimization]]
---

# Question: Which optimization approach?

Task says "optimize video player" but there are 3 approaches:

1. Client-side caching
2. React memoization
3. Web Workers

Which should I implement? Or all three?

## Orchestrator Response
[Claude will update this section]
```

### Claude Gives Direction

**File:** `/notes/orchestrator/direction-002.md`
```markdown
---
tags: #for/codex
task: [[002-video-optimization]]
---

# Direction: Start with React Memoization

@codex - Start with approach #2 (React memoization).

**Why:**
- Fastest to implement
- Lowest risk
- We can add others later if needed

**Scope:**
- Add useMemo for timeline calculations
- Add useCallback for event handlers
- Test performance improvement

**Time limit:** 1 hour max

If you need more than 1 hour, stop and escalate.

#assigned/codex
```

---

## 🚀 Quick Commands for Codex (VS Code)

### Pull Latest Tasks from Claude
```bash
git fetch origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp
git checkout obsidian-vault/tasks/
git merge origin/claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp -- obsidian-vault/tasks/
```

### Check for New Work
```bash
ls obsidian-vault/tasks/delegated/codex/
```

### Complete a Task
```bash
# 1. Move task to active
mv obsidian-vault/tasks/delegated/codex/task.md obsidian-vault/tasks/active/

# 2. Do the work (write code)

# 3. Save artifacts
# (your code files)

# 4. Create note
# obsidian-vault/notes/codex/task.md

# 5. Update task status (edit frontmatter: status: done)

# 6. Move to done
mv obsidian-vault/tasks/active/task.md obsidian-vault/tasks/done/

# 7. Commit on YOUR branch
git checkout -b codex/implementation-2025-01-05
git add .
git commit -m "[codex] Completed task XYZ"
git push origin codex/implementation-2025-01-05
```

---

## 📊 Visual Workflow

```
User creates ticket
       ↓
Claude Web (me!)
  - Analyzes ticket
  - Creates tasks in /tasks/delegated/codex/
  - Commits to claude/ branch
  - Pushes
       ↓
Codex (VS Code)
  - Pulls tasks from claude/ branch
  - Reads task
  - Implements code
  - Saves artifacts
  - Updates task status
  - Commits to codex/ branch
  - Pushes
       ↓
Claude Web (me!)
  - Pulls results from codex/ branch
  - Reviews work
  - Synthesizes final deliverable
  - Updates ticket
  - Done!
```

---

## 🎯 Current Status

**Active Tickets:**
- 000-system-health-check (assigned: Llama, not Codex)
- 001-test-hello-superbeing (assigned: multiple agents)

**Codex's Queue:**
- (empty - waiting for Claude to delegate tasks)

**Next Steps:**
1. Codex: Pull latest vault from Claude's branch
2. Codex: Wait for tasks in `/tasks/delegated/codex/`
3. Claude: Will create tasks as tickets come in

---

## ⚠️ Important Notes

1. **Don't work on same files simultaneously**
   - Claude touches vault coordination
   - Codex touches source code
   - Communicate via notes

2. **Always use separate branches**
   - Prevents merge conflicts
   - Easy to review each agent's work

3. **Tag for attention**
   - `#needs/codex` - Codex should look at this
   - `#needs/orchestrator` - Claude should review

4. **Stay in scope**
   - Codex: Only implement what's in the task
   - Claude: Only orchestrate, don't code

---

**This coordination protocol prevents conflicts and keeps both agents productive!** 🚀
