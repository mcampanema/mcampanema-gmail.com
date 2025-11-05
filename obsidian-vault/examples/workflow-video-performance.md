# Example Workflow: Optimize Video Player Performance

This is a complete walkthrough of how a ticket flows through the SuperBeing multi-agent system.

## Scenario

User reports: "Video player is laggy when seeking. Need to optimize performance."

---

## Step 1: User Creates Ticket

**File:** `/tickets/inbox/003-video-performance.md`

```markdown
---
id: 003-video-performance
created: 2024-01-15 10:00:00
priority: high
type: bug
status: pending
assigned: null
estimated_cost: $0.00
actual_cost: $0.00
agents_used: []
---

# Optimize Video Player Performance

## Description

Users report significant lag when seeking through videos, especially on longer videos (>30min).
Scrubbing the timeline causes frame drops and UI freezes.

## Context

**Related Files:**
- VideoPlayer.tsx
- Visual3D.ts

**User Reports:**
- "Takes 2-3 seconds to seek"
- "Timeline scrubbing is janky"
- "CPU usage spikes to 100%"

## Acceptance Criteria

- [ ] Seeking completes in <500ms
- [ ] No UI freezes during seek
- [ ] CPU usage stays under 50%
- [ ] Works smoothly on 60min+ videos

## Constraints

**Time Limit:** 1 day
**Budget Limit:** $1.00
**Must Use:** Start with Gemini for analysis (cheap), only use CCskills if needed
```

**Commit:**
```bash
git add tickets/inbox/003-video-performance.md
git commit -m "Add ticket: Optimize video player performance"
git push
```

---

## Step 2: Orchestrator Analyzes

**Claude Web** pulls and analyzes:

```bash
cd obsidian-vault
git pull
python3 ../scripts/orchestrator.py --vault . --ticket 003-video-performance.md
```

**Analysis Output:**
```
🔍 Analyzing ticket complexity...
  Complexity: high
  Recommended agents: gemini, codex
  Estimated cost: $0.30
```

---

## Step 3: Claude Web Decomposes

**YOU (Claude) manually decompose:**

```python
from pathlib import Path
import sys
sys.path.append('../scripts')
from orchestrator import create_task_note, move_ticket, create_orchestrator_note

vault_path = Path(".")
ticket = {
    'path': 'tickets/inbox/003-video-performance.md',
    'metadata': {
        'id': '003-video-performance',
        'priority': 'high',
        'type': 'bug'
    },
    'body': '...'
}

analysis = {
    'complexity': 'high',
    'recommended_agents': ['gemini', 'codex'],
    'estimated_cost': 0.30
}

tasks = [
    {
        'subtask_id': '001',
        'agent': 'gemini',
        'title': 'Profile VideoPlayer component',
        'objective': 'Identify performance bottlenecks using Chrome DevTools profiling',
        'estimated_time': '30min',
        'max_time': '45 minutes',
        'exit_criteria': '- [ ] CPU profile captured\n- [ ] Top 5 bottlenecks identified\n- [ ] Flame graph analyzed',
        'files': 'VideoPlayer.tsx\nVisual3D.ts',
        'output_format': 'markdown report with screenshots',
        'artifact_dir': 'reports',
        'must_include': '- List of bottlenecks with line numbers\n- CPU time breakdown\n- Memory usage analysis',
        'agent_instructions': 'Focus ONLY on profiling. Do NOT implement fixes. Attach profiler screenshots.'
    },
    {
        'subtask_id': '002',
        'agent': 'gemini',
        'title': 'Research React performance patterns',
        'objective': 'Find best practices for optimizing heavy rendering in React',
        'estimated_time': '20min',
        'max_time': '30 minutes',
        'exit_criteria': '- [ ] 3-5 relevant patterns documented\n- [ ] Code examples provided',
        'files': 'VideoPlayer.tsx',
        'output_format': 'markdown report',
        'artifact_dir': 'reports',
        'must_include': '- useMemo examples\n- useCallback examples\n- React.memo examples',
        'agent_instructions': 'Quick research only. Do NOT write full tutorials.'
    },
    {
        'subtask_id': '003',
        'agent': 'codex',
        'title': 'Implement memoization in VideoPlayer',
        'objective': 'Add useMemo/useCallback to expensive operations identified by Gemini',
        'estimated_time': '60min',
        'max_time': '90 minutes',
        'exit_criteria': '- [ ] useMemo added for expensive calculations\n- [ ] useCallback added for event handlers\n- [ ] No functionality broken',
        'files': 'VideoPlayer.tsx',
        'output_format': 'updated VideoPlayer.tsx',
        'artifact_dir': 'code',
        'must_include': '- Modified VideoPlayer.tsx\n- Comments explaining optimizations',
        'agent_instructions': 'ONLY optimize bottlenecks from task 001. Do NOT refactor entire file. Wait for task 001 completion.'
    },
    {
        'subtask_id': '004',
        'agent': 'llama',
        'title': 'Verify performance improvements',
        'objective': 'Test seeking performance after optimizations',
        'estimated_time': '20min',
        'max_time': '30 minutes',
        'exit_criteria': '- [ ] Seek time measured (before/after)\n- [ ] CPU usage measured (before/after)\n- [ ] Acceptance criteria checked',
        'files': 'VideoPlayer.tsx',
        'output_format': 'markdown test report',
        'artifact_dir': 'reports',
        'must_include': '- Before/after metrics\n- Pass/fail for each acceptance criterion',
        'agent_instructions': 'Simple testing only. Manual testing OK (no need for automated tests).'
    }
]

for task_data in tasks:
    create_task_note(vault_path, ticket, task_data)

# Move ticket to active
moved_ticket = move_ticket(ticket['path'], vault_path, 'active')

# Create coordination note
create_orchestrator_note(vault_path, ticket, analysis, tasks)
```

**Commit:**
```bash
git add tasks/ tickets/ notes/
git commit -m "[orchestrator] Decomposed 003-video-performance into 4 tasks"
git push
```

---

## Step 4: Gemini Agent Executes Task 001

**Local machine runs:**
```bash
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent gemini --once
```

**Gemini's work:**

1. Reads task from `/tasks/delegated/gemini/003-video-performance-001.md`
2. Calls Gemini Flash API with prompt including task details
3. Gemini analyzes VideoPlayer.tsx and identifies:
   - Heavy render on every seek (line 145)
   - No memoization of timeline calculations (line 89)
   - Expensive Visual3D re-renders (line 201)
4. Saves artifact: `/artifacts/reports/003-video-performance-001-output.md`
5. Creates agent note: `/notes/gemini/003-video-performance-001.md`
6. Updates task status to `done`
7. Moves task to `/tasks/done/`

**Artifact created:**

**File:** `/artifacts/reports/003-video-performance-001-output.md`

```markdown
# Performance Profile: VideoPlayer Component

**Agent:** gemini
**Date:** 2024-01-15 11:15:23
**Task:** [[003-video-performance-001]]

---

## Top 5 Bottlenecks

### 1. Timeline Calculations (45% of CPU time)
**File:** VideoPlayer.tsx:89
**Issue:** calculateTimelinePosition() runs on every render
**Severity:** HIGH

### 2. Visual3D Re-renders (30% of CPU time)
**File:** Visual3D.ts:201
**Issue:** Component re-renders on every parent update
**Severity:** HIGH

### 3. Event Handler Recreation (15% of CPU time)
**File:** VideoPlayer.tsx:145
**Issue:** New handleSeek function created every render
**Severity:** MEDIUM

### 4. Video Metadata Parsing (8% of CPU time)
**File:** VideoPlayer.tsx:312
**Issue:** parseMetadata called multiple times unnecessarily
**Severity:** MEDIUM

### 5. State Updates in Loop (2% of CPU time)
**File:** VideoPlayer.tsx:234
**Issue:** setState called inside forEach loop
**Severity:** LOW

## CPU Time Breakdown

- Timeline calculations: 450ms
- Visual3D rendering: 300ms
- Event handlers: 150ms
- Metadata parsing: 80ms
- State updates: 20ms

**Total:** ~1000ms per seek operation

## Memory Usage

- Baseline: 120MB
- During seek: Spikes to 340MB
- Garbage collection: Every 3-4 seeks

## Recommendations

1. Wrap calculateTimelinePosition in useMemo with [duration, currentTime] deps
2. Memoize Visual3D with React.memo
3. Wrap handleSeek in useCallback
4. Cache parseMetadata results

---

**Status:** Analysis complete
**Cost:** $0.02
```

**Git commit:**
```bash
git add artifacts/ notes/gemini/ tasks/
git commit -m "[gemini] Completed profiling of VideoPlayer"
git push
```

---

## Step 5: Gemini Executes Task 002 (in parallel with 001)

Same process, produces:

**File:** `/artifacts/reports/003-video-performance-002-output.md`

```markdown
# React Performance Patterns

## 1. useMemo for Expensive Calculations

...examples...

## 2. useCallback for Event Handlers

...examples...

## 3. React.memo for Component Memoization

...examples...
```

---

## Step 6: Codex Waits for Dependencies

Task 003 depends on task 001, so Codex agent waits.

Once 001 is done and pushed, Codex picks up 003:

```bash
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent codex --once
```

**Codex's work:**

1. Reads task 003
2. Reads Gemini's output from 001 (knows what to optimize)
3. Calls OpenAI Codex API
4. Generates optimized VideoPlayer.tsx
5. Saves to `/artifacts/code/003-video-performance-003-VideoPlayer.tsx`

**Artifact:**

```typescript
// artifacts/code/003-video-performance-003-VideoPlayer.tsx

import React, { useMemo, useCallback } from 'react';

export function VideoPlayer({ duration, metadata }: VideoPlayerProps) {
  // OPTIMIZATION 1: Memoize timeline calculations
  const timelinePosition = useMemo(() => {
    return calculateTimelinePosition(duration, currentTime);
  }, [duration, currentTime]);

  // OPTIMIZATION 2: Memoize event handlers
  const handleSeek = useCallback((time: number) => {
    setCurrentTime(time);
    videoRef.current?.seekTo(time);
  }, []);

  // OPTIMIZATION 3: Memoize metadata parsing
  const parsedMetadata = useMemo(() => {
    return parseMetadata(metadata);
  }, [metadata]);

  return (
    <div>
      {/* ...UI using optimized values... */}
      <Visual3DMemo /> {/* React.memo wrapper */}
    </div>
  );
}

// OPTIMIZATION 4: Memoize Visual3D component
const Visual3DMemo = React.memo(Visual3D);
```

**Commit:**
```bash
git add artifacts/code/ notes/codex/
git commit -m "[codex] Optimized VideoPlayer with memoization"
git push
```

---

## Step 7: Llama Verifies Results

```bash
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent llama --once
```

**Llama's work:**

Simple testing, produces:

**File:** `/artifacts/reports/003-video-performance-004-output.md`

```markdown
# Performance Verification Report

## Test Results

| Metric | Before | After | Goal | Pass? |
|--------|--------|-------|------|-------|
| Seek time | 1200ms | 380ms | <500ms | ✅ |
| UI freeze | Yes (2s) | No | None | ✅ |
| CPU usage | 95% | 42% | <50% | ✅ |
| 60min video | Laggy | Smooth | Smooth | ✅ |

## Acceptance Criteria

- [x] Seeking completes in <500ms → 380ms ✅
- [x] No UI freezes during seek → Tested OK ✅
- [x] CPU usage stays under 50% → 42% avg ✅
- [x] Works smoothly on 60min+ videos → Tested 90min video ✅

**ALL CRITERIA MET** ✅

## Notes

Performance improvements are significant. User experience is noticeably better.
```

---

## Step 8: Orchestrator Synthesizes

**Claude Web** checks status:

```bash
cd obsidian-vault
git pull
ls tasks/done/
# 003-video-performance-001.md
# 003-video-performance-002.md
# 003-video-performance-003.md
# 003-video-performance-004.md
```

All done! Now synthesize:

**File:** `/artifacts/003-video-performance-FINAL.md`

```markdown
# Video Player Performance Optimization - Complete

**Ticket:** [[003-video-performance]]
**Date:** 2024-01-15 14:30:00
**Status:** ✅ COMPLETE

## Summary

Successfully optimized VideoPlayer component, reducing seek time from 1.2s to 380ms.

## Work Completed

### Analysis (Gemini)
- [[003-video-performance-001-output]] - Performance profiling
- [[003-video-performance-002-output]] - React patterns research

### Implementation (Codex)
- [[003-video-performance-003-VideoPlayer.tsx]] - Optimized component

### Verification (Llama)
- [[003-video-performance-004-output]] - Test results

## Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Seek time | 1200ms | 380ms | **68% faster** |
| CPU usage | 95% | 42% | **56% reduction** |
| Memory | Spikes to 340MB | Stable at 180MB | **47% reduction** |

## Changes Made

1. Added `useMemo` for timeline calculations
2. Added `useCallback` for event handlers
3. Memoized Visual3D component with `React.memo`
4. Cached metadata parsing results

## Files Modified

- `VideoPlayer.tsx` - See [[003-video-performance-003-VideoPlayer.tsx]]

## Cost Breakdown

- Gemini (2 tasks): $0.03
- Codex (1 task): $0.25
- Llama (1 task): $0.00
- **Total: $0.28** (under $1.00 budget ✅)

## Time Breakdown

- Analysis: 50 min
- Implementation: 60 min
- Verification: 20 min
- **Total: 2h 10min** (under 1 day budget ✅)

## Acceptance Criteria

- [x] Seeking completes in <500ms
- [x] No UI freezes during seek
- [x] CPU usage stays under 50%
- [x] Works smoothly on 60min+ videos

**ALL CRITERIA MET** ✅

## Next Steps

1. Deploy to staging
2. Monitor for regressions
3. Consider additional optimizations if needed:
   - Web Workers for heavy calculations
   - Virtual scrolling for timeline
   - Lazy loading for video metadata

## Lessons Learned

- React memoization is powerful but must be used strategically
- Profiling first (Gemini) prevented premature optimization
- Breaking work into focused tasks kept costs low
```

**Update ticket:**

```bash
# Edit tickets/active/003-video-performance.md
# Update status to done
# Reference final deliverable

mv tickets/active/003-video-performance.md tickets/done/
```

**Commit:**
```bash
git add artifacts/ tickets/
git commit -m "[orchestrator] Synthesized final deliverable for 003-video-performance"
git push
```

---

## Step 9: Claude Web Publishes to Repo

**If changes need to go back to code repo:**

```bash
# Copy optimized file to actual repo
cp obsidian-vault/artifacts/code/003-video-performance-003-VideoPlayer.tsx ../VideoPlayer.tsx

cd ..
git add VideoPlayer.tsx
git commit -m "perf: Optimize VideoPlayer seek performance

- Add useMemo for timeline calculations
- Add useCallback for event handlers
- Memoize Visual3D component
- Cache metadata parsing

Reduces seek time from 1.2s to 380ms (68% faster).
Resolves ticket obsidian-vault#003-video-performance"

git push -u origin claude/web-code-remote-worker-011CUqTjXYrmGharUpFohfFp
```

---

## Final State

```
obsidian-vault/
├── tickets/
│   ├── inbox/           (empty)
│   ├── active/          (empty)
│   └── done/
│       └── 003-video-performance.md ✅
├── tasks/
│   ├── delegated/       (all empty)
│   ├── active/          (empty)
│   └── done/
│       ├── 003-video-performance-001.md ✅
│       ├── 003-video-performance-002.md ✅
│       ├── 003-video-performance-003.md ✅
│       └── 003-video-performance-004.md ✅
├── notes/
│   ├── gemini/
│   │   ├── 003-video-performance-001.md
│   │   └── 003-video-performance-002.md
│   ├── codex/
│   │   └── 003-video-performance-003.md
│   ├── llama/
│   │   └── 003-video-performance-004.md
│   └── orchestrator/
│       └── coord-003-video-performance.md
├── artifacts/
│   ├── reports/
│   │   ├── 003-video-performance-001-output.md
│   │   ├── 003-video-performance-002-output.md
│   │   └── 003-video-performance-004-output.md
│   ├── code/
│   │   └── 003-video-performance-003-VideoPlayer.tsx
│   └── 003-video-performance-FINAL.md
└── decisions/
    └── (none needed for this ticket)
```

---

## Metrics

**Total Cost:** $0.28
**Total Time:** 2h 10min
**Agents Used:** Gemini (2x), Codex (1x), Llama (1x)
**Success:** ✅ All acceptance criteria met, under budget

---

## What We Learned

1. **Decomposition is key** - Breaking into 4 focused tasks prevented scope creep
2. **Right agent for the job** - Gemini for analysis ($0.02), Codex for implementation ($0.25), Llama for testing ($0.00)
3. **Obsidian kept everyone organized** - Clear task boundaries prevented deep dives
4. **Cost-conscious choices** - Llama for simple testing saved $0.15
5. **Sequential when needed** - Codex waited for Gemini's analysis before optimizing
