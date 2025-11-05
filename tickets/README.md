# Tickets - Task Queue for Claude Web Worker

This directory structure manages queued tasks for the Claude Code Web Worker.

## Directory Structure

```
tickets/
├── inbox/       ← Place new task tickets here (JSON files)
├── processing/  ← Active ticket (moved here when picked up)
└── done/        ← Completed tickets (move here after publishing)
```

## Ticket Format

Each ticket is a JSON file with the following structure:

```json
{
  "id": "unique-identifier",
  "type": "task|question|implementation|analysis|refactor",
  "title": "Short descriptive title",
  "description": "Detailed description of what needs to be done",
  "context": {
    "files": ["path/to/relevant/file.ts"],
    "relevant_docs": ["https://docs.example.com"]
  },
  "priority": "high|medium|low",
  "artifacts": ["expected-output-1.md", "expected-output-2.json"]
}
```

## Field Descriptions

- **id** (required): Unique identifier, used in branch name
- **type**: Category of work
  - `task` - General task
  - `question` - Research or answer a question
  - `implementation` - Build a feature
  - `analysis` - Analyze code or system
  - `refactor` - Code improvement
- **title** (required): Brief summary
- **description** (required): Full details
- **context**: Additional information
  - `files`: Relevant source files to review
  - `relevant_docs`: External documentation
- **priority**: Processing order (high processed first)
- **artifacts**: Expected output files

## Workflow

### 1. Create Ticket

```bash
cat > tickets/inbox/002-optimize-rendering.json <<EOF
{
  "id": "002-optimize-rendering",
  "type": "implementation",
  "title": "Optimize 3D rendering performance",
  "description": "The Visual3D component is causing frame drops. Profile and optimize the rendering pipeline.",
  "context": {
    "files": ["Visual3D.ts", "VideoPlayer.tsx"],
    "relevant_docs": ["https://threejs.org/docs/#manual/en/introduction/Performance-best-practices"]
  },
  "priority": "high",
  "artifacts": ["performance-report.md", "Visual3D.ts"]
}
EOF
```

### 2. Process in Web Worker

Claude Code Web runs:

```bash
python3 scripts/ccsweb_worker.py
```

This:
- Reads the highest-priority ticket from `inbox/`
- Generates `CURRENT_TASK.md` with instructions
- Moves ticket to `processing/`

### 3. Complete Task

Claude follows `CURRENT_TASK.md` instructions and runs:

```bash
python3 scripts/bridge_ccsweb.py "002-optimize-rendering" \
  --artifacts performance-report.md Visual3D.ts
```

### 4. Mark Done

```bash
mv tickets/processing/002-optimize-rendering.json tickets/done/
```

## Example Tickets

### Research Question

```json
{
  "id": "q-001-api-integration",
  "type": "question",
  "title": "How does the Gemini API integration work?",
  "description": "Document the current Gemini API integration, including authentication, request flow, and error handling.",
  "context": {
    "files": ["api.ts", "functions.ts"]
  },
  "priority": "low",
  "artifacts": ["api-integration-guide.md"]
}
```

### Bug Fix

```json
{
  "id": "bug-003-video-seek",
  "type": "task",
  "title": "Fix video seeking bug",
  "description": "Video player crashes when seeking to end of video. Investigate and fix the crash.",
  "context": {
    "files": ["VideoPlayer.tsx"],
    "relevant_docs": ["https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/seeking_event"]
  },
  "priority": "high",
  "artifacts": ["bug-fix-report.md", "VideoPlayer.tsx"]
}
```

### Feature Implementation

```json
{
  "id": "feat-004-export",
  "type": "implementation",
  "title": "Add video export functionality",
  "description": "Implement a feature to export processed video segments with overlays. Should support MP4 format.",
  "context": {
    "files": ["VideoPlayer.tsx", "Visual3D.ts"],
    "relevant_docs": [
      "https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder",
      "https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API"
    ]
  },
  "priority": "medium",
  "artifacts": [
    "export-feature-design.md",
    "ExportManager.ts",
    "VideoPlayer.tsx"
  ]
}
```

## Automation Tips

### Bulk Ticket Creation

```bash
#!/bin/bash
# Create multiple tickets from a list

TASKS=(
  "refactor:low:Refactor Chart component for better readability"
  "task:high:Add error boundaries to prevent app crashes"
  "question:medium:Document the LiveChat protocol"
)

for task in "${TASKS[@]}"; do
  IFS=':' read -r type priority title <<< "$task"
  id=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | cut -c1-30)

  cat > "tickets/inbox/${id}.json" <<EOF
{
  "id": "$id",
  "type": "$type",
  "title": "$title",
  "description": "$title - Details TBD",
  "priority": "$priority",
  "artifacts": ["${id}-report.md"]
}
EOF
done
```

### Priority Queue Monitoring

```bash
# Show pending tickets by priority
find tickets/inbox -name "*.json" -exec jq -r '[.priority, .id, .title] | @tsv' {} \; | sort
```

## Integration with Local Orchestrator

Your local machine's orchestrator can:
1. Generate tickets programmatically
2. Commit tickets to `inbox/`
3. Push to trigger web worker
4. Monitor for results via `gh_watch.py`

Example orchestrator pseudo-code:

```python
# Orchestrator detects need for analysis
ticket = create_ticket(
    id="auto-" + timestamp,
    type="analysis",
    title="Security audit of new feature",
    files=changed_files
)

save_ticket(ticket, "tickets/inbox/")
git_commit_and_push()

# gh_watch.py monitors and pulls results
# Orchestrator consumes from out/ccsweb/
```

## See Also

- `scripts/ccsweb_worker.py` - Ticket processor
- `scripts/bridge_ccsweb.py` - Result publisher
- `CLAUDE.md` - Instructions for web worker
