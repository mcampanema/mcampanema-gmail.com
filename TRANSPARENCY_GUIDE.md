# AI Transparency System - Complete Guide

**Created:** 2025-11-08
**Purpose:** See EXACTLY what AI agents are doing, thinking, and saying to each other.

---

## 🔥 WHAT YOU NOW HAVE:

### ✅ **1. AI Cost Tracker** (`scripts/ai_transparency_logger.py`)
- Logs EVERY AI API call
- Tracks costs per model
- Shows input/output tokens
- Full prompt and response logging

### ✅ **2. Real-Time Dashboard** (`scripts/ai_dashboard.py`)
- Visual display of all AI activity
- Cost breakdown by model
- Daily spending reports
- Recent activity feed

### ✅ **3. Multi-Agent Memory** (`scripts/multi_agent_memory.py`)
- Shared memory between AI agents
- AI-to-AI conversations logged
- Thought process tracking
- Decision reasoning

### ✅ **4. Conversation Viewer** (`scripts/view_ai_conversations.py`)
- See what AIs say to each other
- View agent thought processes
- Understand decision making
- Access shared knowledge

### ✅ **5. API Key Audit** (`scripts/api_key_audit.sh`)
- Shows which API keys are configured
- Identifies missing keys
- Security check for exposed secrets

### ✅ **6. Monitored API Wrappers** (`scripts/monitored_gemini.py`)
- Auto-logging Gemini API wrapper
- Auto-logging Claude API wrapper
- Drop-in replacement for direct API usage

---

## 🚀 QUICK START

### Check What API Keys You Have

```bash
bash scripts/api_key_audit.sh
```

**CURRENT STATUS:** No API keys configured in environment.
**NEXT STEP:** Set `GEMINI_API_KEY` environment variable or create `.env` file.

---

### View AI Activity Dashboard

```bash
python3 scripts/ai_dashboard.py
```

Shows:
- Total API calls made
- Total cost in USD
- Cost by model (Gemini, Claude, etc.)
- Recent activity log
- Daily cost breakdown

---

### See AI Conversations

```bash
# See everything
python3 scripts/view_ai_conversations.py all

# Just conversations between AIs
python3 scripts/view_ai_conversations.py conversations

# Just AI thought processes
python3 scripts/view_ai_conversations.py thoughts

# Just AI decisions
python3 scripts/view_ai_conversations.py decisions

# Just shared memory
python3 scripts/view_ai_conversations.py memory
```

---

## 📋 HOW TO USE IN YOUR CODE

### Replace Direct Gemini Calls

**OLD WAY (No logging):**
```python
from google.generativeai import GenerativeModel

model = GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Analyze this video")
```

**NEW WAY (Auto-logged):**
```python
from scripts.monitored_gemini import MonitoredGeminiAPI

model = MonitoredGeminiAPI("gemini-2.5-flash")
response = model.generate_content(
    "Analyze this video",
    metadata={"task": "video-analysis", "user": "michael"}
)
# Automatically logs: cost, tokens, prompt, response
```

---

### Log AI-to-AI Communication

```python
from scripts.multi_agent_memory import ai_says, ai_thinks, ai_decides

# Claude tells Gemini to do something
ai_says(
    from_agent="claude-orchestrator",
    to_agent="gemini-analyst",
    message="Please analyze this video for anomalies",
    message_type="delegation"
)

# Gemini thinks about it
ai_thinks(
    agent="gemini-analyst",
    thought="I will focus on the first 30 seconds and look for motion spikes",
    thought_type="planning",
    confidence=0.85
)

# Gemini decides on approach
ai_decides(
    agent="gemini-analyst",
    decision="Use frame-by-frame analysis with 250ms intervals",
    reasoning="This provides good coverage without excessive token usage",
    alternatives=["1s intervals (too coarse)", "100ms intervals (too expensive)"]
)

# Gemini responds to Claude
ai_says(
    from_agent="gemini-analyst",
    to_agent="claude-orchestrator",
    message="Analysis complete. Found 3 anomalies. Report attached.",
    message_type="result"
)
```

---

### Update Shared Memory

```python
from scripts.multi_agent_memory import get_memory

memory = get_memory()

# Update shared knowledge
memory.update_context({
    "shared_knowledge": {
        "video_001_analysis": {
            "anomalies": 3,
            "timestamps": ["0:15", "0:22", "0:28"],
            "severity": "medium"
        }
    }
})

# Start a task
memory.start_task(
    task_id="video-002",
    task_description="Analyze security footage for intruders",
    assigned_to="gemini-analyst"
)

# Complete a task
memory.complete_task(
    task_id="video-002",
    result="No intruders detected. 2 animals identified."
)
```

---

## 📊 VIEWING LOGS

All logs are stored in:

```
logs/
├── ai_transparency/          # API call logs
│   ├── session_*.jsonl      # Per-session call logs
│   └── summary.json         # Aggregate statistics
│
└── agent_memory/            # Multi-agent logs
    ├── ai_conversations.jsonl  # AI-to-AI communication
    ├── ai_thoughts.jsonl       # Internal reasoning
    ├── ai_decisions.jsonl      # Decision logs
    └── shared_context.json     # Shared memory
```

---

## 🔑 API KEY CONFIGURATION

### Option 1: Environment Variables (Recommended)

```bash
export GEMINI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-claude-key-here"
```

### Option 2: .env File

Create `.env` in project root:

```bash
GEMINI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-claude-key-here
```

**IMPORTANT:** `.env` is already in `.gitignore` - won't be committed.

### Option 3: Check Current Status

```bash
bash scripts/api_key_audit.sh
```

---

## 💰 COST TRACKING

### View Current Costs

```bash
python3 scripts/ai_dashboard.py
```

### Export Costs to CSV

```bash
python3 scripts/ai_dashboard.py export costs.csv
```

### Model Pricing (Per 1M Tokens)

| Model | Input | Output | Total for 10K input + 10K output |
|-------|-------|--------|----------------------------------|
| Gemini 2.5 Flash | $0.075 | $0.30 | $0.00375 |
| Claude Sonnet 4.5 | $3.00 | $15.00 | $0.18 |
| Claude Opus 4 | $15.00 | $75.00 | $0.90 |
| GPT-4o | $2.50 | $10.00 | $0.125 |
| Llama (local) | $0.00 | $0.00 | $0.00 |

**Strategy:** Use Gemini Flash for cheap analysis, Claude Sonnet for orchestration, Llama for free local processing.

---

## 🔍 REAL-TIME MONITORING

### Watch AI Conversations Live

```bash
# Terminal 1: Run your AI agent
python3 your_agent.py

# Terminal 2: Watch conversations
watch -n 2 "python3 scripts/view_ai_conversations.py conversations | tail -50"
```

### Watch Costs Live

```bash
watch -n 5 "python3 scripts/ai_dashboard.py"
```

---

## 🎯 RECOMMENDED WORKFLOW

### 1. Configure API Keys
```bash
bash scripts/api_key_audit.sh
# Fix any missing keys
```

### 2. Register Your Agents
```python
from scripts.multi_agent_memory import get_memory

memory = get_memory()

memory.register_agent(
    "gemini-vision",
    "Video & Image Analysis",
    ["video_analysis", "image_recognition", "cheap_compute"]
)

memory.register_agent(
    "claude-orchestrator",
    "Task Orchestration & PM",
    ["task_planning", "agent_delegation", "synthesis"]
)

memory.register_agent(
    "llama-local",
    "Local Processing",
    ["offline_compute", "code_generation", "free_processing"]
)
```

### 3. Use Monitored API Calls
```python
from scripts.monitored_gemini import MonitoredGeminiAPI

gemini = MonitoredGeminiAPI("gemini-2.5-flash")
response = gemini.send_message("Your prompt here")
```

### 4. View Results
```bash
# See dashboard
python3 scripts/ai_dashboard.py

# See conversations
python3 scripts/view_ai_conversations.py all
```

---

## 🐛 DEBUGGING

### No Logs Showing Up?

1. Check if API calls are using monitored wrappers
2. Verify log directory exists: `ls -la logs/`
3. Check file permissions: `chmod -R 755 logs/`

### API Keys Not Working?

```bash
# Run audit
bash scripts/api_key_audit.sh

# Check environment
env | grep -i key

# Test .env file loading
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### Conversations Not Logging?

Make sure you're using the logging functions:

```python
from scripts.multi_agent_memory import ai_says, ai_thinks, ai_decides

# NOT this:
# print("Agent X says Y")  # Won't be logged

# Instead:
ai_says("agent-x", "agent-y", "message", "request")  # Will be logged
```

---

## 📚 ADVANCED FEATURES

### Custom Model Pricing

Edit `scripts/ai_transparency_logger.py`:

```python
PRICING = {
    "your-custom-model": {"input": 0.10, "output": 0.50},
    # ...existing models
}
```

### Export for Obsidian

```python
# Create markdown reports
from scripts.view_ai_conversations import load_conversations
import json

convos = load_conversations()
with open("ai_conversations.md", "w") as f:
    for conv in convos:
        f.write(f"## {conv['timestamp']}\n")
        f.write(f"**{conv['from']}** → **{conv['to']}**\n\n")
        f.write(f"{conv['message']}\n\n---\n\n")
```

---

## 🎓 LEARNING RESOURCES

Based on web search (2025-11-08):

### YouTube Tutorials
- **LangChain YouTube**: Multi-agent workflow walkthroughs
- **AutoGen Tutorials**: Multi-agent conversations (200K+ users)
- **CrewAI Demos**: Team-based agent collaboration

### Frameworks to Explore
1. **LangGraph** - Graph-based orchestration with thought process visibility
2. **AutoGen** - Conversational multi-agent (most popular)
3. **CrewAI** - Team-based collaboration (easiest to start)

### Key Articles Found
- "Multi-Agent Orchestration & Conversations using Autogen, CrewAI and LangGraph" (Medium)
- "Building AI Agents That Actually Remember" (Medium)
- "LangGraph: Multi-Agent Workflows" (LangChain Blog)

---

## ❓ FAQ

**Q: Why are there no logs yet?**
A: Logs are created when AI API calls are made. Run a test first.

**Q: Where are costs tracked?**
A: `logs/ai_transparency/summary.json`

**Q: Can I see what AIs are thinking?**
A: Yes! Use `ai_thinks()` function and view with `view_ai_conversations.py thoughts`

**Q: How do I share memory between agents?**
A: Use `memory.update_context()` and `memory.get_context()`

**Q: Is this tracking Claude Code (this session)?**
A: No, this is for tracking external AI API calls (Gemini, Claude API, etc.). Claude Code Web conversations are separate.

**Q: What's the cheapest model?**
A: Llama (local, free) > Gemini Flash ($0.075-0.30/1M) > GPT-4o-mini ($0.15-0.60/1M)

---

## 🔄 NEXT STEPS

1. ✅ **Set up API keys** - Run `bash scripts/api_key_audit.sh`
2. ✅ **Test logging** - Run `python3 scripts/multi_agent_memory.py` (demo)
3. ✅ **View dashboard** - Run `python3 scripts/ai_dashboard.py`
4. ✅ **Integrate into your code** - Replace direct API calls with monitored wrappers
5. ✅ **Monitor costs** - Check dashboard daily
6. ✅ **Review conversations** - See what AIs are saying to each other

---

## 🎉 YOU NOW HAVE:

- ✅ Full transparency into AI operations
- ✅ Cost tracking per model
- ✅ AI-to-AI conversation logs
- ✅ Thought process visibility
- ✅ Shared memory between agents
- ✅ Decision reasoning logs
- ✅ Real-time monitoring
- ✅ Export capabilities

**NO MORE "WEIRD MADE UP STORIES" - Just Facts.**

---

**Questions? Check logs at `logs/` or run dashboard commands.**
