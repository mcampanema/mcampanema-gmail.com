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

## SuperBeing Multi-Agent Stack

This repo is the **coordination hub** for a multi-agent AI system powered by **Obsidian**.

### Architecture

```
                User
                 │
                 ▼
          Obsidian Vault ← Central nervous system
          (Git-synced)      All agents coordinate here
                 │
     ┌───────────┼───────────┬──────────┐
     ▼           ▼           ▼          ▼
  Gemini      Codex      CCskills    Llama
  (cheap)     (code)     (smart)     (free!)
     │           │           │          │
     └───────────┴───────────┴──────────┘
                 │
                 ▼
        Claude Web (Orchestrator/PM)
        - Breaks down tickets
        - Delegates to agents
        - Synthesizes results
        - Prevents deep dives
                 │
                 ▼
          Final Artifacts
```

### Why Obsidian?

- **Shared memory** - All agents read/write markdown
- **Clear boundaries** - Task scopes prevent rabbit holes
- **Audit trail** - Every decision documented
- **Knowledge graph** - Backlinks create context
- **Version control** - Git tracks everything
- **Cost tracking** - See exactly what each agent costs

### Quick Start

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup guide.**

**TL;DR:**

```bash
# 1. Set up API keys
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key

# 2. Start executive agents (local machine)
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent gemini --api-key $GEMINI_API_KEY &
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent codex --api-key $OPENAI_API_KEY &
python3 scripts/agent_worker.py --vault obsidian-vault/ --agent llama &

# 3. Create a ticket
cp obsidian-vault/templates/ticket.md obsidian-vault/tickets/inbox/my-task.md
# Edit and commit

# 4. Run orchestrator (Claude Code Web at claude.ai/code)
cd obsidian-vault
python3 ../scripts/orchestrator.py --vault .
# Then manually decompose as Claude Web
```

### How It Works

1. **User** creates ticket in `obsidian-vault/tickets/inbox/`
2. **Claude Web** (orchestrator) analyzes and decomposes into subtasks
3. **Executive agents** poll for tasks and execute them
4. **Obsidian** keeps everyone organized and on-task
5. **Claude Web** synthesizes final deliverable
6. **No deep dives** - Clear scope and time limits on every task

### Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[obsidian-vault/README.md](obsidian-vault/README.md)** - Vault structure
- **[obsidian-vault/PROTOCOL.md](obsidian-vault/PROTOCOL.md)** - Coordination protocol
- **[obsidian-vault/examples/](obsidian-vault/examples/)** - Complete workflow examples
- **[CLAUDE.md](CLAUDE.md)** - Instructions for Claude Web orchestrator
- **[scripts/README.md](scripts/README.md)** - Script documentation

### Cost Optimization

**Agent Selection Strategy:**

1. **Llama (Local)** - FREE! Use first for simple tasks
2. **Gemini Flash** - $0.01-0.05 - Fast analysis, summaries
3. **Codex** - $0.10-0.50 - Code generation, implementation
4. **CCskills (Claude CLI)** - $0.50-2.00 - Complex reasoning, architecture

**Example costs:**
- Simple ticket: $0.00 (Llama only)
- Medium ticket: $0.15 (Gemini + Codex)
- Complex ticket: $1.50 (All agents)
