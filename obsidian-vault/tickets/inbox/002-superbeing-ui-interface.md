---
id: 002-superbeing-ui-interface
created: 2025-01-05 21:30:00
priority: high
type: feature
status: pending
assigned: codex
estimated_cost: $2.00
actual_cost: $0.00
agents_used: []
---

# SuperBeing UI Interface for VS Code

## Description

Build a visual UI interface that makes it easy for Codex (and other agents in VS Code) to operate the SuperBeing system without command-line operations.

**Why this is awesome:**
- Visual task queue (see what needs to be done)
- One-click task pickup
- Easy status updates
- Communication with Claude Web
- Progress tracking
- Cost monitoring
- **Meta**: Using SuperBeing to build a better SuperBeing!

## Context

**Current workflow (command-line):**
```bash
git fetch origin claude/...
git merge origin/claude/... -- obsidian-vault/
dir obsidian-vault\tasks\delegated\codex\
# Manual task processing...
```

**Desired workflow (UI):**
- Open VS Code panel
- See task list visually
- Click "Pick up task"
- Code with inline task details
- Click "Mark complete"
- Auto-commit and sync

## Acceptance Criteria

### Phase 1: Basic Dashboard (MVP)
- [ ] VS Code webview panel showing task queue
- [ ] List tasks from `/obsidian-vault/tasks/delegated/codex/`
- [ ] Show task details (title, priority, time limit, scope)
- [ ] Button: "Pick up this task" (moves to active)
- [ ] Show active task with countdown timer
- [ ] Button: "Mark complete" (moves to done)
- [ ] Auto-commit and push when task completed

### Phase 2: Communication
- [ ] See messages from Claude Web
- [ ] Create escalation/question notes
- [ ] Tag with #needs/orchestrator-review
- [ ] Visual notification when Claude responds

### Phase 3: Progress & Analytics
- [ ] Task progress bar
- [ ] Time tracking per task
- [ ] Cost estimate vs actual
- [ ] Daily summary stats

### Phase 4: Polish
- [ ] Dark mode support
- [ ] Keyboard shortcuts
- [ ] Task filtering (priority, status)
- [ ] Search tasks

## Design Mockup

```
┌─────────────────────────────────────────────────┐
│  🤖 SuperBeing Control Panel                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  📥 Task Queue (3)                   🔄 Sync   │
│  ┌──────────────────────────────────────────┐  │
│  │ 🔴 HIGH │ 002-dark-mode-001              │  │
│  │         │ Implement dark mode toggle     │  │
│  │         │ ⏱️  1 hour | 💰 $0.30          │  │
│  │         │ [Pick up task]                 │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ 🟡 MED  │ 003-api-integration-001        │  │
│  │         │ Connect to Gemini API          │  │
│  │         │ ⏱️  45 min | 💰 $0.20          │  │
│  │         │ [Pick up task]                 │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ⚙️  Active Task                                │
│  ┌──────────────────────────────────────────┐  │
│  │ 001-video-optimization                    │  │
│  │ Progress: 65% ████████░░░░░               │  │
│  │ Time remaining: 21 minutes                │  │
│  │                                           │  │
│  │ 📋 Scope:                                 │  │
│  │ ✅ Add useMemo for calculations           │  │
│  │ ✅ Add useCallback for handlers           │  │
│  │ ⏳ Test performance                       │  │
│  │                                           │  │
│  │ [View Details] [Mark Complete] [Help]    │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  💬 Messages from Claude (1)                   │
│  ┌──────────────────────────────────────────┐  │
│  │ 🟦 "Good progress! Focus on performance  │  │
│  │     testing next. Let me know if you     │  │
│  │     need more time." - 2 min ago         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  📊 Today's Stats                               │
│  Tasks completed: 2 | Time: 1.5h | Cost: $0.45 │
└─────────────────────────────────────────────────┘
```

## Technical Approach

### Option 1: VS Code Extension (RECOMMENDED)
**Pros:**
- Native integration
- Access to VS Code APIs
- Can open files directly
- Better UX

**Tech Stack:**
- TypeScript
- VS Code Extension API
- Webview for UI
- Git commands via child_process

**Files:**
```
vscode-extension/
├── package.json
├── extension.ts          # Main extension
├── taskPanel.ts          # Webview panel
├── gitSync.ts            # Git operations
└── webview/
    ├── index.html
    ├── styles.css
    └── app.js
```

### Option 2: Standalone Web App
**Pros:**
- Works outside VS Code
- Can be used by any agent
- Easier to build

**Tech Stack:**
- React or vanilla JS
- Local file system access
- Git operations

### Option 3: VS Code Task Provider
**Pros:**
- Uses VS Code's built-in task system
- Minimal UI

**Cons:**
- Less flexible
- Not as visual

## Implementation Plan

### Phase 1: Core Functionality (Day 1-2)
**Tasks:**
1. Create VS Code extension boilerplate
2. Read tasks from `obsidian-vault/tasks/delegated/codex/`
3. Display task list in webview
4. Implement "pick up task" (move file)
5. Show active task details
6. Implement "mark complete" (move to done)
7. Basic git sync (pull/push)

**Deliverables:**
- Working extension (unpublished)
- Can view and process tasks
- Git sync works

### Phase 2: Communication (Day 3)
**Tasks:**
1. Show messages from `/notes/orchestrator/`
2. Create question/escalation notes
3. Auto-tag with proper metadata
4. Notification when Claude responds

**Deliverables:**
- Two-way communication working
- Visual alerts for new messages

### Phase 3: Analytics (Day 4)
**Tasks:**
1. Parse task metadata for time/cost
2. Track time spent per task
3. Calculate daily stats
4. Show progress indicators

**Deliverables:**
- Time tracking
- Cost estimation
- Daily summary

### Phase 4: Polish (Day 5)
**Tasks:**
1. Add dark mode
2. Keyboard shortcuts
3. Task filtering/search
4. Error handling
5. Documentation

**Deliverables:**
- Production-ready extension
- User documentation

## Constraints

**Time Limit:** 5 days max
**Budget Limit:** $2.00
**Must Use:**
- Codex for implementation (dogfooding!)
- Gemini for research/design
- Claude Web for coordination

**Technology Constraints:**
- Must work offline (local git operations)
- No external API dependencies
- Pure TypeScript/JavaScript

## Expected Output

### Deliverables
1. **VS Code Extension Package**
   - `/artifacts/code/superbeing-vscode-extension/`
   - Installable .vsix file

2. **Documentation**
   - `/artifacts/reports/002-ui-user-guide.md`
   - Installation instructions
   - Usage guide
   - Screenshots

3. **Demo Video/Screenshots**
   - `/artifacts/diagrams/002-ui-demo.gif`
   - Show task pickup flow

4. **Source Code**
   - All TypeScript files
   - Tests
   - README

## Success Metrics

- [ ] Codex can use UI instead of command-line
- [ ] Task pickup takes < 5 seconds (was 2+ minutes with CLI)
- [ ] Zero git conflicts
- [ ] Visual progress tracking works
- [ ] Communication with Claude Web works

## Future Enhancements (Out of Scope)

- Multi-agent support (Gemini, Llama views)
- Web-based dashboard (not just VS Code)
- Real-time collaboration
- Obsidian plugin integration
- Mobile app
- Voice commands

## Notes

**This is meta and awesome!**
- We're using SuperBeing to build SuperBeing
- Codex will implement the UI they'll use
- Tests the full workflow
- Makes the system way easier to use

**Priority: HIGH** because this will make all future work easier!

## References

- VS Code Extension Docs: https://code.visualstudio.com/api
- Webview API: https://code.visualstudio.com/api/extension-guides/webview
- Git from Node.js: Use `child_process` or `simple-git` library
- Task markdown format: See `/templates/task.md`

---

**Let's build this and make SuperBeing super easy to use!** 🚀
