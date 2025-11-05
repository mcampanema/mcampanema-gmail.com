# Claude Code Web Worker - Scripts

This directory contains the bridge infrastructure for using Claude Code on the Web as a remote worker in your SuperBeing multi-agent stack.

## Scripts Overview

### `install_pkgs.sh`
**Runs on:** Web Worker VM (automatically via SessionStart hook)
**Purpose:** Initial VM setup - configures git, creates directories

### `bridge_ccsweb.py`
**Runs on:** Web Worker VM (invoked by Claude)
**Purpose:** Publishes artifacts and pushes results to `ccsweb/*` branch

**Usage:**
```bash
python3 scripts/bridge_ccsweb.py "task-name" --artifacts file1.md file2.json
```

### `gh_watch.py`
**Runs on:** Your local machine (VS Code task or terminal)
**Purpose:** Monitors for `ccsweb/*` branches and pulls artifacts locally

**Usage:**
```bash
# Basic usage
python3 scripts/gh_watch.py

# With custom settings
python3 scripts/gh_watch.py \
  --interval 30 \
  --out-dir ./out/ccsweb \
  --obsidian-vault ~/Obsidian/SuperBeing

# Run once (no loop)
python3 scripts/gh_watch.py --once
```

**Options:**
- `--interval SECONDS` - Check interval (default: 60)
- `--out-dir DIR` - Output directory (default: `./out/ccsweb`)
- `--obsidian-vault DIR` - Obsidian vault path (optional)
- `--once` - Run once and exit
- `--prefix PREFIX` - Branch prefix to watch (default: `ccsweb/`)

### `ccsweb_worker.py`
**Runs on:** Web Worker VM (invoked by Claude or manually)
**Purpose:** Processes queued tasks from `tickets/inbox/*.json`

**Usage:**
```bash
python3 scripts/ccsweb_worker.py
```

## Quick Start

### 1. Setup (One-time)

On your local machine, start the watcher:

```bash
python3 scripts/gh_watch.py --out-dir ./out/ccsweb --obsidian-vault ~/path/to/vault
```

### 2. Queue a Task

Create a ticket in `tickets/inbox/`:

```bash
cat > tickets/inbox/001-example.json <<EOF
{
  "id": "001-example",
  "type": "task",
  "title": "Analyze video player performance",
  "description": "Profile the VideoPlayer component and identify bottlenecks",
  "context": {
    "files": ["VideoPlayer.tsx"]
  },
  "priority": "high",
  "artifacts": ["performance-analysis.md"]
}
EOF
```

### 3. Process in Web Worker

In Claude Code Web, run:

```bash
python3 scripts/ccsweb_worker.py
```

This generates `CURRENT_TASK.md` with instructions. Complete the task, then run the bridge command shown.

### 4. Results Appear Locally

The local watcher automatically:
- Fetches the new `ccsweb/*` branch
- Copies artifacts to `out/ccsweb/`
- Updates Obsidian vault (if configured)

## Integration with SuperBeing Stack

The local watcher feeds into your orchestrator:

```
┌─────────────────┐
│ Claude Code Web │ ──┐
│   (Remote VM)   │   │
└─────────────────┘   │
                      │ git push ccsweb/*
                      ▼
              ┌──────────────┐
              │  GitHub Repo │
              └──────────────┘
                      │
                      │ git fetch
                      ▼
              ┌──────────────┐
              │  gh_watch.py │ ◄── Runs on local machine
              │   (Watcher)  │
              └──────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    out/ccsweb/  Obsidian    Drive Sync
                  Vault
                      │
                      ▼
              ┌──────────────┐
              │ Orchestrator │
              │ (SuperBeing) │
              └──────────────┘
```

## Environment Variables

Set in `.claude/settings.json` or Web UI Environment settings:

```json
{
  "environment": {
    "CCS_WEB_BRANCH_PREFIX": "ccsweb/",
    "CCS_WEB_ART_DIR": "ccsweb_artifacts"
  }
}
```

## Security

- **No secrets in repo** - `.env` is gitignored
- **Limited network** - Keep `allowNetworkAccess: false` unless needed
- **Separate credits** - Web worker uses web credits, not API billing
- **Branch permissions** - Only `claude/*` branches can be pushed

## Troubleshooting

### Watcher not finding branches

```bash
# Manually check for branches
git fetch origin
git branch -r | grep ccsweb

# Verify watcher state
cat out/ccsweb/.processed_branches.json
```

### Bridge push fails

- Ensure branch starts with `claude/` and ends with session ID
- Check network permissions
- Verify git credentials

### Tickets not processing

- Validate JSON syntax
- Check file is in `tickets/inbox/`
- Run with Python directly: `python3 scripts/ccsweb_worker.py`

## Advanced Usage

### Custom Artifact Processing

Modify `gh_watch.py` to add custom processing:

```python
def process_branch(branch_name, out_dir, obsidian_vault=None):
    # ... existing code ...

    # Add custom logic here
    # E.g., trigger Drive sync, update database, send notification
```

### Multiple Repo Workers

Run separate watchers for different repos:

```bash
# Terminal 1 - Repo A
cd ~/projects/repo-a
python3 scripts/gh_watch.py --out-dir ./out/ccsweb-a

# Terminal 2 - Repo B
cd ~/projects/repo-b
python3 scripts/gh_watch.py --out-dir ./out/ccsweb-b
```

### CI/CD Integration

Create GitHub Action to auto-open PR for `ccsweb/*` branches:

```yaml
name: Auto-PR for Claude Web Worker
on:
  push:
    branches:
      - 'ccsweb/*'
jobs:
  create-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create PR
        run: |
          gh pr create --title "🤖 Claude Web Worker Results" \
            --body "Automated results from Claude Code Web Worker"
```

## See Also

- `CLAUDE.md` - Instructions for Claude in the web worker
- `.claude/settings.json` - Web worker configuration
- `tickets/` - Task queue directory structure
