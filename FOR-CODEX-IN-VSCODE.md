# 📋 Instructions for Codex (VS Code)

**Role:** Executive Agent - Code Implementation
**Coordinates with:** Claude Code Web (Orchestrator)
**Communication:** Obsidian vault in this repo

---

## 🎯 Your Job

You implement code tasks that Claude Web delegates to you.

**Workflow:**
1. Pull tasks from `/obsidian-vault/tasks/delegated/codex/`
2. Implement the code
3. Save results to `/obsidian-vault/artifacts/code/`
4. Update task status
5. Commit to your own branch (`codex/implementation-<date>`)

---

## 🔧 Setup (One Time)

### Create Your Branch
```bash
git checkout -b codex/implementation-2025-01-05
git push -u origin codex/implementation-2025-01-05
```

### Set Your Working Branch
```bash
git checkout codex/implementation-2025-01-05
```

---

## 🔄 Checking for New Tasks

### Pull Latest from Claude's Branch
```bash
# Fetch what Claude created
git fetch origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp

# Merge ONLY the vault folder (not other files)
git merge origin/claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp -- obsidian-vault/
```

### Check Your Queue
```bash
# See if there are tasks for you
dir obsidian-vault\tasks\delegated\codex\
```

**If you see `.md` files → You have work!**

---

## 📝 Processing a Task

### 1. Read the Task
```bash
# Open the task file
code obsidian-vault\tasks\delegated\codex\002-task-name-001.md
```

**Key sections to read:**
- **Objective** - What to build
- **Scope** - What's IN vs OUT
- **Time Limit** - Max time to spend
- **Exit Criteria** - When you're done
- **Expected Output** - What to create

### 2. Move to Active
```bash
move obsidian-vault\tasks\delegated\codex\002-task-name-001.md obsidian-vault\tasks\active\
```

### 3. Do the Work

**Example - Implementing a component:**
```typescript
// VideoPlayer.tsx
import React, { useMemo, useCallback } from 'react';

export function VideoPlayer() {
  // Your implementation here
  // Follow the task's requirements
}
```

### 4. Save Artifacts

**Code files:**
```bash
# Save to artifacts for Claude to review
copy VideoPlayer.tsx obsidian-vault\artifacts\code\002-task-name-001-VideoPlayer.tsx
```

### 5. Create Agent Note

**File:** `obsidian-vault\notes\codex\002-task-name-001.md`

```markdown
---
agent: codex
date: 2025-01-05 14:30:00
task: [[002-task-name-001]]
cost: $0.25
---

# Codex - Video Player Optimization

## Task
Implemented memoization for VideoPlayer component.

## What I Did
1. Added useMemo for timeline calculations (line 45)
2. Added useCallback for event handlers (line 67)
3. Wrapped Visual3D in React.memo (line 89)

## Results
- Code saved to /artifacts/code/002-task-name-001-VideoPlayer.tsx
- All requirements met
- Tested locally - works!

## For Orchestrator
Ready for review. No blockers.

#status/done
```

### 6. Update Task Status

Edit the task file's frontmatter:
```markdown
---
status: done  # Change from "active" to "done"
completed: 2025-01-05 14:45:00  # Add completion time
---
```

### 7. Move to Done
```bash
move obsidian-vault\tasks\active\002-task-name-001.md obsidian-vault\tasks\done\
```

### 8. Commit Your Work
```bash
# Stage everything
git add .

# Commit with clear message
git commit -m "[codex] Implemented VideoPlayer optimization (task 002-001)

- Added useMemo for timeline calculations
- Added useCallback for event handlers
- React.memo wrapper for Visual3D
- Artifact: 002-task-name-001-VideoPlayer.tsx"

# Push to YOUR branch
git push origin codex/implementation-2025-01-05
```

---

## 🚨 If You Need Help

### Ask Claude (Orchestrator)

**Create:** `obsidian-vault\notes\codex\question-002.md`

```markdown
---
tags: #needs/orchestrator-review
task: [[002-task-name]]
---

# Question: Need Clarification

I'm working on task 002-001 but unclear about [specific issue].

**Options I see:**
1. Approach A - [describe]
2. Approach B - [describe]

Which should I use?

## Orchestrator Response
[Claude will update this section]
```

**Then commit and push** - Claude will see it on next sync.

---

## ⏱️ If You Hit Time Limit

### Escalate, Don't Continue

**Create:** `obsidian-vault\notes\codex\escalation-002.md`

```markdown
---
tags: #needs/orchestrator-review
task: [[002-task-name]]
---

# Escalation: Task Taking Longer Than Expected

Task 002-001 has 30min time limit but I've hit it.

**Progress:**
- ✅ Completed steps 1-3
- ❌ Step 4 blocked by [issue]
- ⏳ Steps 5-6 not started

**Need Decision:**
- Extend time limit? (will cost more)
- Reduce scope? (skip steps 5-6)
- Different approach?

**Recommendation:** [your suggestion]
```

**Stop work, commit what you have, wait for direction.**

---

## 🎯 Best Practices

### ✅ Do
- Stay within task scope
- Respect time limits
- Update task status regularly
- Create clear agent notes
- Commit often to YOUR branch
- Ask if unclear

### ❌ Don't
- Work on multiple tasks simultaneously
- Exceed time limit without escalating
- Commit to Claude's branch
- Skip creating agent notes
- Change scope without asking
- Work without a task assignment

---

## 📊 Branch Strategy

```
main
  ├── claude/web-code-remote-worker-... (Claude's orchestration)
  └── codex/implementation-2025-01-05   (Your code work)
```

**Why separate branches?**
- Prevents merge conflicts
- Easy to review each agent's work
- User can merge when ready

---

## 🔄 Daily Workflow

### Morning: Pull Tasks
```bash
git fetch origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp
git merge origin/claude/... -- obsidian-vault/
dir obsidian-vault\tasks\delegated\codex\
```

### During Day: Process Tasks
1. Read task
2. Move to active
3. Implement
4. Create note
5. Update status
6. Move to done
7. Commit & push

### Evening: Report Progress
Create daily summary in `obsidian-vault\notes\codex\daily-2025-01-05.md`

```markdown
# Codex Daily Summary - 2025-01-05

## Tasks Completed
- [[002-001]] - VideoPlayer optimization
- [[003-001]] - Chart component refactor

## Tasks In Progress
- [[004-001]] - API integration (60% done)

## Blockers
- None

## Notes
Good progress today. API integration needs 1 more hour tomorrow.
```

---

## 🆘 Troubleshooting

### "Merge conflict in obsidian-vault"
```bash
# Claude changed same file - rare but possible
# Accept THEIR changes (Claude is orchestrator)
git checkout --theirs obsidian-vault/tasks/...
git add .
git commit
```

### "Can't find tasks"
```bash
# Make sure you pulled from Claude's branch
git fetch --all
git log origin/claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp --oneline
```

### "Don't know what to work on"
Check:
1. `/obsidian-vault/tasks/delegated/codex/` - Your assigned tasks
2. `/obsidian-vault/notes/orchestrator/` - Claude's direction
3. If empty, wait for Claude to assign tasks

---

## 📞 Current Status

**Coordination Protocol:** obsidian-vault/COORDINATION-CLAUDE-CODEX.md

**Your Branch:** `codex/implementation-2025-01-05`

**Claude's Branch:** `claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp`

**Communication Channel:** Obsidian vault (git-synced)

---

**You're ready!** Wait for Claude to delegate tasks, then process them using the workflow above. 🚀
