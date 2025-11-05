<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# GEMINI 3DAPEX BARDII BEST

An interactive video player that lets you summarize, describe scenes, extract text, search for objects, and more.

View your app in AI Studio: https://ai.studio/apps/drive/1yLG8u9VTTrrKeHwNFcNIkeGdab6REg_r

## Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

## Claude Code Web Worker

This repo is configured as a **remote worker** in the SuperBeing multi-agent stack.

### Quick Start

**On your local machine:**

```bash
# Start the watcher (pulls results from web worker)
python3 scripts/gh_watch.py --out-dir ./out/ccsweb --obsidian-vault ~/path/to/vault
```

**In Claude Code Web (claude.ai/code):**

```bash
# Process queued tasks
python3 scripts/ccsweb_worker.py

# Or manually publish results after completing a task
python3 scripts/bridge_ccsweb.py "task-name" --artifacts report.md
```

### How It Works

1. **Queue tasks** by creating JSON tickets in `tickets/inbox/`
2. **Process in web worker** - Claude picks up tickets and completes tasks
3. **Results auto-sync** - Local watcher pulls artifacts to `out/ccsweb/` and Obsidian
4. **Orchestrator integrates** - SuperBeing feeds results into the multi-agent pipeline

### Documentation

- **[CLAUDE.md](CLAUDE.md)** - Instructions for the web worker agent
- **[scripts/README.md](scripts/README.md)** - Detailed script documentation
- **[tickets/README.md](tickets/README.md)** - Task queue system guide

### Architecture

```
Local Machine          GitHub           Cloud Worker
     │                   │                   │
     │  git push         │                   │
     ├──────tickets─────>│                   │
     │                   │   git clone       │
     │                   │◄──────────────────┤
     │                   │                   │
     │                   │   ┌─────────────┐ │
     │                   │   │ Process task│ │
     │                   │   └─────────────┘ │
     │                   │                   │
     │                   │   git push ccsweb/*
     │                   │◄──────────────────┤
     │  git fetch        │                   │
     │◄────ccsweb/*──────┤                   │
     │                   │                   │
     v                   │                   │
out/ccsweb/             │                   │
Obsidian/               │                   │
Drive/                  │                   │
```
