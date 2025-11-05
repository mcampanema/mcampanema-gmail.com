#!/usr/bin/env python3
"""
SuperBeing Executive Agent Worker

This script is run by EACH executive agent (Gemini, CCskills, Codex, Llama).
It polls for tasks in /tasks/delegated/{agent}/, executes them, and reports back.

Usage:
    # Gemini agent
    python3 scripts/agent_worker.py --vault /path/to/vault --agent gemini --api-key $GEMINI_API_KEY

    # Local Llama
    python3 scripts/agent_worker.py --vault /path/to/vault --agent llama --local

    # One-shot mode (process one task and exit)
    python3 scripts/agent_worker.py --vault /path/to/vault --agent codex --once
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import subprocess


def load_task(task_path):
    """Load and parse a task markdown file."""
    with open(task_path, 'r') as f:
        content = f.read()

    # Parse frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            body = parts[2].strip()

            metadata = {}
            for line in frontmatter_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            return {
                'metadata': metadata,
                'body': body,
                'path': task_path
            }

    return None


def update_task_status(task_path, status, notes=""):
    """Update task status in frontmatter and add progress note."""
    with open(task_path, 'r') as f:
        content = f.read()

    # Update status in frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        frontmatter = parts[1]
        body = parts[2]

        # Update status line
        frontmatter = '\n'.join([
            f"status: {status}" if line.startswith('status:') else line
            for line in frontmatter.split('\n')
        ])

        # Add timestamp for started/completed
        if status == 'active' and 'started: null' in frontmatter:
            frontmatter = frontmatter.replace(
                'started: null',
                f"started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        elif status == 'done' and 'completed: null' in frontmatter:
            frontmatter = frontmatter.replace(
                'completed: null',
                f"completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        # Add progress note
        progress_note = f"\n\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**Status:** {status}\n{notes}\n"

        content = f"---{frontmatter}---{body}{progress_note}"

        with open(task_path, 'w') as f:
            f.write(content)


def move_task(task_path, vault_path, destination):
    """Move task to active or done folder."""
    task_file = Path(task_path)
    dest_dir = Path(vault_path) / 'tasks' / destination
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / task_file.name
    os.rename(task_path, dest_path)

    return dest_path


def call_agent_api(agent, prompt, api_key=None):
    """
    Call the specified agent's API.
    This is a STUB - you'll implement actual API calls.
    """
    if agent == 'gemini':
        # TODO: Implement Gemini Flash API call
        return f"[STUB] Gemini Flash response to: {prompt[:100]}..."

    elif agent == 'ccskills':
        # TODO: Implement Claude CLI call
        return f"[STUB] Claude CLI response to: {prompt[:100]}..."

    elif agent == 'codex':
        # TODO: Implement OpenAI Codex API call
        return f"[STUB] Codex response to: {prompt[:100]}..."

    elif agent == 'llama':
        # TODO: Implement local Llama call (ollama, llama.cpp, etc.)
        return f"[STUB] Llama local response to: {prompt[:100]}..."

    else:
        return f"[ERROR] Unknown agent: {agent}"


def execute_task(task, agent, vault_path, api_key=None):
    """
    Execute a task by calling the agent's API.
    Returns the output path.
    """
    print(f"  🤖 Executing task with {agent}...")

    # Extract key info from task
    objective = task['metadata'].get('id', 'unknown task')
    body = task['body']

    # Build prompt for agent
    prompt = f"""You are the {agent} agent in the SuperBeing multi-agent stack.

Task ID: {task['metadata'].get('id')}
Objective: {objective}

Task Details:
{body}

IMPORTANT:
- Stay within scope
- Respect time limit: {task['metadata'].get('estimated_time', '30min')}
- Stop at exit criteria
- Output to the specified artifact location

Please complete this task and provide your output.
"""

    # Call agent API
    response = call_agent_api(agent, prompt, api_key)

    # Save output as artifact
    task_id = task['metadata'].get('id', 'task')
    artifact_dir = Path(vault_path) / 'artifacts' / 'reports'
    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = artifact_dir / f"{task_id}-output.md"

    with open(artifact_path, 'w') as f:
        f.write(f"""# {task_id} Output

**Agent:** {agent}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Task:** [[{Path(task['path']).stem}]]

---

{response}

---

**Status:** Completed by {agent}
""")

    print(f"  ✓ Artifact saved: {artifact_path}")

    # Create agent note
    note_dir = Path(vault_path) / 'notes' / agent
    note_dir.mkdir(parents=True, exist_ok=True)

    note_path = note_dir / f"{task_id}.md"

    with open(note_path, 'w') as f:
        f.write(f"""---
agent: {agent}
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
task: [[{Path(task['path']).stem}]]
cost: $0.00
---

# {agent.title()} - {task_id}

## Task

**Assigned:** [[{Path(task['path']).stem}]]
**Started:** {task['metadata'].get('started', 'N/A')}
**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** done

## Findings

See artifact: [[{artifact_path.name}]]

## Approach

1. Analyzed task requirements
2. Executed according to scope
3. Generated output artifact

## Results

**Artifacts Created:**
- `/artifacts/reports/{artifact_path.name}`

## Status Update

- [x] Task completed
- [x] Artifacts saved to `/artifacts/`
- [x] Task note updated with status
- [x] Ready to move to `/tasks/done/`

Next: Orchestrator will synthesize results.
""")

    print(f"  ✓ Agent note created: {note_path}")

    return artifact_path


def main():
    parser = argparse.ArgumentParser(description="SuperBeing Executive Agent Worker")
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--agent', required=True, choices=['gemini', 'ccskills', 'codex', 'llama'],
                        help='Agent name')
    parser.add_argument('--api-key', help='API key for agent (if needed)')
    parser.add_argument('--once', action='store_true', help='Process one task and exit')
    parser.add_argument('--interval', type=int, default=30, help='Polling interval in seconds')

    args = parser.parse_args()

    vault_path = Path(args.vault)
    delegated_dir = vault_path / 'tasks' / 'delegated' / args.agent

    print(f"🤖 SuperBeing Agent: {args.agent.upper()}")
    print(f"📁 Vault: {vault_path}")
    print(f"📂 Task queue: {delegated_dir}")
    if args.once:
        print("🔄 Mode: One-shot")
    else:
        print(f"🔄 Mode: Continuous (polling every {args.interval}s)")
    print()

    iteration = 0
    while True:
        iteration += 1
        print(f"🔍 Check #{iteration} at {datetime.now().strftime('%H:%M:%S')}")

        # Find pending tasks
        tasks = list(delegated_dir.glob('*.md')) if delegated_dir.exists() else []

        if not tasks:
            print("  📭 No tasks")
        else:
            print(f"  📬 Found {len(tasks)} task(s)")

            # Process first task
            task_path = tasks[0]
            print(f"  📝 Processing: {task_path.name}")

            task = load_task(task_path)
            if not task:
                print(f"    ❌ Failed to parse task")
                continue

            # Update status to active
            update_task_status(task_path, 'active', f"**Agent:** {args.agent}\nTask started")

            # Move to active folder
            active_path = move_task(task_path, vault_path, 'active')
            print(f"    → Moved to active: {active_path}")

            # Execute task
            try:
                artifact_path = execute_task(task, args.agent, vault_path, args.api_key)

                # Update status to done
                task['path'] = active_path  # Update path after move
                update_task_status(active_path, 'done', f"**Output:** [[{artifact_path.name}]]")

                # Move to done folder
                done_path = move_task(active_path, vault_path, 'done')
                print(f"    ✓ Completed: {done_path}")

            except Exception as e:
                print(f"    ❌ Error: {e}")
                update_task_status(active_path, 'blocked', f"**Error:** {e}")

        if args.once:
            print("\n✓ One-shot complete")
            break

        print(f"💤 Sleeping {args.interval}s...\n")
        time.sleep(args.interval)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped")
        sys.exit(0)
