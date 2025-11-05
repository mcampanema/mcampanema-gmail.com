# Claude Code Web Worker Instructions

Welcome, Claude! You are running as a **remote worker** in the Claude Code Web environment.

This repository is part of a **multi-agent SuperBeing stack** that combines:
- Local Llama models
- Gemini Flash API (CLI)
- Claude API (selective)
- **You** (Claude Code Web) as a distributed worker

## Your Role

You process tasks remotely and publish results back to the orchestrator via git branches.

## Automatic Setup

When this session starts, `.claude/settings.json` triggers `scripts/install_pkgs.sh` to:
- ✓ Set up git config
- ✓ Create `ccsweb_artifacts/` directory
- ✓ Verify Python3 and git are available

## How to Process Tasks

### Manual Task Flow

When given a task manually (via chat or prompt):

1. **Complete the task** using your normal workflow
2. **Collect outputs** into files (markdown reports, JSON summaries, code changes, etc.)
3. **Publish results** using the bridge:

```bash
python3 scripts/bridge_ccsweb.py "task-name" --artifacts file1.md file2.json
```

Example:
```bash
# After fixing video controls and writing a report
python3 scripts/bridge_ccsweb.py "fix-video-controls" --artifacts out/report.md src/VideoPlayer.tsx
```

This will:
- Copy artifacts to `ccsweb_artifacts/`
- Create a manifest with metadata
- Commit changes
- Create a new branch like `ccsweb/1699123456-fix-video-controls`
- Push to origin
- Return to the original branch

### Automatic Ticket Processing

For automated task queues, check for tickets:

```bash
python3 scripts/ccsweb_worker.py
```

This will:
- Look for JSON tickets in `tickets/inbox/`
- Process the highest priority ticket
- Generate `CURRENT_TASK.md` with instructions
- Move ticket to `tickets/processing/`

After completing the task:
1. Run the bridge command (shown in CURRENT_TASK.md)
2. Move ticket to done: `mv tickets/processing/ticket.json tickets/done/`

## Ticket Format

Create tickets as JSON in `tickets/inbox/`:

```json
{
  "id": "001-optimize-video",
  "type": "implementation",
  "title": "Optimize video rendering performance",
  "description": "The video player lags when seeking. Profile and fix performance bottlenecks.",
  "context": {
    "files": ["VideoPlayer.tsx", "Visual3D.ts"],
    "relevant_docs": ["https://react.dev/reference/react/useMemo"]
  },
  "priority": "high",
  "artifacts": ["out/profile-report.md", "src/VideoPlayer.tsx"]
}
```

## Local Orchestrator Integration

Your published branches are monitored by a **local watcher** (`scripts/gh_watch.py`) that:
- Fetches `ccsweb/*` branches every 60s (configurable)
- Copies artifacts to `out/ccsweb/`
- Exports markdown to Obsidian vault
- Triggers Drive sync
- Feeds results back into the SuperBeing orchestrator

## Environment Variables

Set these in `.claude/settings.json` or Web UI:

- `CCS_WEB_BRANCH_PREFIX` (default: `ccsweb/`) - Branch prefix for results
- `CCS_WEB_ART_DIR` (default: `ccsweb_artifacts`) - Artifact directory name

## Security & Billing

- **Network**: Keep `allowNetworkAccess: false` unless specifically needed
- **Credits**: Web Claude Code uses separate credits (not API billing)
- **Secrets**: Avoid committing `.env` or credentials

## Best Practices

1. **Always use the bridge** - Don't manually push branches; use `bridge_ccsweb.py`
2. **Clear artifact naming** - Use descriptive filenames (e.g., `video-performance-report.md`)
3. **Include context in reports** - Mention file paths, line numbers, decisions made
4. **Test before publishing** - If fixing bugs, verify the fix works
5. **Clean commits** - The bridge creates clean commit messages; don't clutter history

## Example Workflows

### Research Task

```bash
# Task: Analyze codebase for security vulnerabilities
# 1. Perform analysis
# 2. Write report
# 3. Publish
python3 scripts/bridge_ccsweb.py "security-audit" --artifacts security-report.md
```

### Implementation Task

```bash
# Task: Add dark mode toggle
# 1. Implement feature
# 2. Write tests
# 3. Document changes
# 4. Publish
python3 scripts/bridge_ccsweb.py "dark-mode-feature" \
  --artifacts \
    implementation-notes.md \
    src/DarkModeToggle.tsx \
    tests/DarkModeToggle.test.tsx
```

### Question/Analysis

```bash
# Task: How does the 3D visualization work?
# 1. Read Visual3D.ts and related files
# 2. Document architecture
# 3. Create diagrams if helpful
# 4. Publish
python3 scripts/bridge_ccsweb.py "3d-viz-analysis" --artifacts analysis.md architecture.svg
```

## Troubleshooting

### Bridge fails to push

- Check network settings (may need `allowNetworkAccess: true` temporarily)
- Verify git credentials
- Branch name must start with `claude/` and end with session ID for push to work

### No tickets found

- Tickets must be in `tickets/inbox/*.json`
- Validate JSON syntax
- Check file permissions

### Artifacts not copied

- Ensure artifact files exist before running bridge
- Use relative or absolute paths
- Check file permissions

## Questions?

If you (Claude) are unsure about a task or need clarification:
1. Ask in the chat - the human operator is watching
2. Document assumptions in your reports
3. Use the bridge to publish partial results with questions

---

**Remember:** You are part of a **distributed agent network**. Your work here feeds into a larger orchestration system. Make your outputs clear, structured, and machine-readable so the local orchestrator can process them effectively.

**Have fun building! 🚀**
