# SuperBeing Multi-Agent Stack - Quick Start

Welcome! This guide gets you up and running with the **Obsidian-powered multi-agent coordination system**.

## Architecture Overview

```
       YOU (User)
           │
           ▼
    Obsidian Vault ← Central coordination system
    (Git-synced)
           │
    ┌──────┴──────┐
    ▼             ▼
Orchestrator   Executive Agents
(Claude Web)   (Gemini, Codex, CCskills, Llama)
    │             │
    └──────┬──────┘
           ▼
    Final Artifacts
```

## Prerequisites

- **Python 3.8+**
- **Git**
- **Obsidian** (optional but recommended)
- **API keys** for agents you want to use:
  - `GEMINI_API_KEY` - Google Gemini Flash
  - `OPENAI_API_KEY` - OpenAI Codex
  - `ANTHROPIC_API_KEY` - Claude CLI (CCskills)

## Step 1: Set Up Obsidian Vault

### Option A: Use Included Vault

```bash
cd mcampanema-gmail.com/

# Initialize the vault as a git repo (if not already)
cd obsidian-vault
git init
git add .
git commit -m "Initial SuperBeing vault"

# Optional: Push to your own remote
git remote add origin YOUR_VAULT_REPO_URL
git push -u origin main
```

### Option B: Link to Existing Obsidian Vault

```bash
cd mcampanema-gmail.com/

# Remove example vault
rm -rf obsidian-vault

# Symlink to your existing vault
ln -s ~/Documents/Obsidian/MyVault obsidian-vault

# Copy SuperBeing structure into your vault
cp -r obsidian-vault-template/* ~/Documents/Obsidian/MyVault/SuperBeing/
```

## Step 2: Configure API Keys

```bash
# Create .env file (not committed to git)
cat > .env <<EOF
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
EOF

# Load in shell
export $(cat .env | xargs)
```

## Step 3: Create Your First Ticket

```bash
# Use the template
cp obsidian-vault/templates/ticket.md obsidian-vault/tickets/inbox/001-my-first-task.md

# Edit it
vim obsidian-vault/tickets/inbox/001-my-first-task.md
```

**Example ticket:**

```markdown
---
id: 001-hello-world
created: 2024-01-15 10:00:00
priority: medium
type: task
status: pending
---

# Test SuperBeing Stack

## Description

Create a simple "Hello World" test to verify all agents can communicate.

## Acceptance Criteria

- [ ] Gemini agent responds
- [ ] Codex agent responds
- [ ] Llama agent responds

## Constraints

**Budget Limit:** $0.10
```

**Commit:**

```bash
cd obsidian-vault
git add tickets/inbox/001-hello-world.md
git commit -m "Add first test ticket"
git push
```

## Step 4: Start Agent Workers (Local Machine)

Open **4 terminal windows**:

### Terminal 1: Gemini

```bash
cd mcampanema-gmail.com
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent gemini \
  --api-key $GEMINI_API_KEY
```

### Terminal 2: Codex

```bash
cd mcampanema-gmail.com
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent codex \
  --api-key $OPENAI_API_KEY
```

### Terminal 3: Llama (Local - Free!)

```bash
cd mcampanema-gmail.com
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent llama
```

### Terminal 4: CCskills (Optional - Expensive)

Only start this if you have high-complexity tasks:

```bash
cd mcampanema-gmail.com
python3 scripts/agent_worker.py \
  --vault obsidian-vault/ \
  --agent ccskills \
  --api-key $ANTHROPIC_API_KEY
```

## Step 5: Run Orchestrator (Claude Code Web)

Go to **claude.ai/code**, select this repo, and start a session.

The `.claude/settings.json` hook will auto-run setup.

Then:

```bash
cd obsidian-vault
python3 ../scripts/orchestrator.py --vault .
```

This analyzes the ticket and **pauses** for YOU (Claude Web) to manually decompose it.

## Step 6: Decompose Manually (You = Claude Web)

Follow the orchestrator's instructions to break down the ticket:

```python
# Example decomposition
tasks = [
    {
        'subtask_id': '001',
        'agent': 'gemini',
        'title': 'Say hello from Gemini',
        'objective': 'Return a simple "Hello from Gemini!" message',
        'estimated_time': '5min',
        'max_time': '10 minutes',
        'exit_criteria': '- [ ] Message returned',
        'files': '',
        'output_format': 'markdown',
        'artifact_dir': 'reports'
    },
    # ... similar for codex, llama
]

from pathlib import Path
import sys
sys.path.append('../scripts')
from orchestrator import create_task_note, move_ticket, create_orchestrator_note

vault_path = Path(".")
for task_data in tasks:
    create_task_note(vault_path, ticket, task_data)

move_ticket(ticket['path'], vault_path, 'active')
create_orchestrator_note(vault_path, ticket, analysis, tasks)
```

**Commit:**

```bash
git add tasks/ tickets/ notes/
git commit -m "[orchestrator] Decomposed 001-hello-world"
git push
```

## Step 7: Watch Agents Work

Back in your local terminals, you'll see:

**Terminal 1 (Gemini):**
```
🔍 Check #2 at 10:05:23
  📬 Found 1 task(s)
  📝 Processing: 001-hello-world-001.md
    → Moved to active
  🤖 Executing task with gemini...
  ✓ Artifact saved: artifacts/reports/001-hello-world-001-output.md
  ✓ Agent note created: notes/gemini/001-hello-world-001.md
    ✓ Completed
```

**Terminal 2 (Codex):**
```
🔍 Check #2 at 10:05:28
  📬 Found 1 task(s)
  📝 Processing: 001-hello-world-002.md
...
```

## Step 8: Synthesize Results (Claude Web)

Once all tasks are done, check back in Claude Web:

```bash
cd obsidian-vault
git pull
ls tasks/done/
# All tasks should be here
```

Create final deliverable:

```markdown
# Test Complete: Hello World

All agents responded successfully! ✅

## Results

- Gemini: "Hello from Gemini!" ($0.01)
- Codex: "Hello from Codex!" ($0.05)
- Llama: "Hello from Llama!" ($0.00)

**Total Cost:** $0.06 (under $0.10 budget)
```

Save to `/artifacts/001-hello-world-FINAL.md`, commit, push.

## Step 9: View in Obsidian (Optional)

Open Obsidian → Open vault → Select `obsidian-vault/`

You'll see:
- Tickets with status badges
- Task breakdowns with links
- Agent notes interlinked
- Full knowledge graph

Use **Graph View** to see connections!

## Tips

### Cost Optimization

1. **Start with Llama** (free) for simple tasks
2. **Use Gemini** (cheap) for analysis/summaries
3. **Use Codex** (moderate) for code generation
4. **Use CCskills** (expensive) only for complex reasoning

### Preventing Deep Dives

Each task has:
- **Time limit** - Agent must stop
- **Scope** - What's IN vs OUT
- **Exit criteria** - When to call it done

Agents escalate if they need more time/scope.

### Monitoring Costs

```bash
# Check artifact metadata
grep "Cost:" obsidian-vault/notes/*/*.md | awk '{sum+=$2} END {print "Total: $" sum}'
```

### Parallel vs Sequential

- **Parallel:** Independent tasks (analysis + research)
- **Sequential:** Dependent tasks (profile → optimize)

Orchestrator can create tasks with dependencies.

## Troubleshooting

### "No tasks found"

- Check tasks are in `/tasks/delegated/{agent}/`
- Verify git repo is synced
- Agent might be looking at wrong vault path

### "API key error"

- Verify `export GEMINI_API_KEY=...` worked
- Check `.env` file exists and is loaded
- API key might be expired/invalid

### "Obsidian vault not found"

- Ensure `obsidian-vault/` exists
- Check path in `--vault` argument
- Try absolute path instead of relative

### "Tasks stuck in active"

- Agent might have crashed
- Check agent terminal for errors
- Manually move task back to delegated: `mv tasks/active/task.md tasks/delegated/{agent}/`

## Next Steps

1. **Read the full protocol:** `obsidian-vault/PROTOCOL.md`
2. **See a complete example:** `obsidian-vault/examples/workflow-video-performance.md`
3. **Customize templates:** `obsidian-vault/templates/`
4. **Set up GitHub Actions:** Auto-process tickets on push

## Getting Help

- Check `obsidian-vault/README.md` for vault structure
- Read `CLAUDE.md` for instructions to Claude Web
- See `scripts/README.md` for script documentation

---

**You're ready!** Start with a simple ticket and work your way up to complex multi-agent workflows. 🚀
