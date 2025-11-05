#!/usr/bin/env python3
"""
SuperBeing Orchestrator - Claude Code Web as PM

This script is run BY Claude Code Web to:
1. Process tickets from Obsidian vault
2. Decompose into subtasks
3. Delegate to executive agents
4. Monitor progress
5. Synthesize results

Usage:
    python3 scripts/orchestrator.py --vault /path/to/obsidian-vault
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import argparse


def load_ticket(ticket_path):
    """Load and parse a ticket markdown file."""
    with open(ticket_path, 'r') as f:
        content = f.read()

    # Parse frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            body = parts[2].strip()

            # Parse YAML frontmatter (simple parsing)
            frontmatter = {}
            for line in frontmatter_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

            return {
                'metadata': frontmatter,
                'body': body,
                'path': ticket_path
            }

    return None


def analyze_ticket_complexity(ticket):
    """
    Analyze ticket to determine:
    - Which agents needed
    - Estimated cost
    - Task breakdown suggestions
    """
    body = ticket['body'].lower()
    metadata = ticket['metadata']

    analysis = {
        'recommended_agents': [],
        'estimated_cost': 0.0,
        'complexity': 'medium',
        'suggested_tasks': []
    }

    # Keyword detection for agent selection
    if any(word in body for word in ['implement', 'create', 'build', 'add feature', 'write code']):
        analysis['recommended_agents'].append('codex')
        analysis['estimated_cost'] += 0.10

    if any(word in body for word in ['analyze', 'review', 'audit', 'security', 'performance']):
        analysis['recommended_agents'].append('ccskills')
        analysis['estimated_cost'] += 0.05

    if any(word in body for word in ['summarize', 'document', 'explain', 'how does']):
        analysis['recommended_agents'].append('gemini')
        analysis['estimated_cost'] += 0.01

    # Default to Llama for simple tasks
    if not analysis['recommended_agents']:
        analysis['recommended_agents'].append('llama')
        analysis['estimated_cost'] = 0.0

    # Complexity assessment
    acceptance_criteria = body.count('- [ ]')
    if acceptance_criteria > 5:
        analysis['complexity'] = 'high'
        analysis['estimated_cost'] *= 2
    elif acceptance_criteria <= 2:
        analysis['complexity'] = 'low'
        analysis['estimated_cost'] *= 0.5

    return analysis


def create_task_note(vault_path, ticket, task_data):
    """Create a task note in the delegated agent folder."""
    agent = task_data['agent']
    task_id = f"{ticket['metadata'].get('id', 'task')}-{task_data['subtask_id']}"

    task_dir = Path(vault_path) / 'tasks' / 'delegated' / agent
    task_dir.mkdir(parents=True, exist_ok=True)

    task_file = task_dir / f"{task_id}.md"

    content = f"""---
id: {task_id}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ticket: [[{Path(ticket['path']).stem}]]
agent: {agent}
status: pending
priority: {ticket['metadata'].get('priority', 'medium')}
estimated_time: {task_data.get('estimated_time', '30min')}
started: null
completed: null
---

# {task_data['title']}

## Objective

{task_data['objective']}

## Scope

**IN SCOPE:**
{task_data.get('in_scope', '- (see objective)')}

**OUT OF SCOPE:**
- Do NOT refactor unrelated code
- Do NOT implement features beyond this task
- Do NOT spend more than the time limit

## Time Limit

**Maximum:** {task_data.get('max_time', '30 minutes')}

If you hit this limit, STOP and create an escalation note in `/notes/{agent}/escalation-{task_id}.md` tagged with `#needs/orchestrator-review`.

## Exit Criteria

You are DONE when:
{task_data['exit_criteria']}

## Context

**Parent Ticket:** [[{Path(ticket['path']).stem}]]

**Relevant Files:**
```
{task_data.get('files', 'N/A')}
```

**Background:**
{task_data.get('background', 'See parent ticket for full context.')}

## Expected Output

**Format:** {task_data.get('output_format', 'markdown report')}

**Location:** `/artifacts/{task_data.get('artifact_dir', 'reports')}/{task_id}-output.md`

**Must Include:**
{task_data.get('must_include', '- Summary of findings\n- Recommendations')}

## Agent Instructions

### For {agent.title()}

{task_data.get('agent_instructions', 'Follow standard procedures for this task type.')}

## Progress Updates

### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Created by orchestrator
**Next Step:** Agent picks up from `/tasks/delegated/{agent}/`
"""

    with open(task_file, 'w') as f:
        f.write(content)

    print(f"  ✓ Created task: {task_file}")
    return task_file


def move_ticket(ticket_path, vault_path, destination):
    """Move ticket to active or done folder."""
    ticket_file = Path(ticket_path)
    dest_dir = Path(vault_path) / 'tickets' / destination
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / ticket_file.name
    os.rename(ticket_path, dest_path)

    return dest_path


def create_orchestrator_note(vault_path, ticket, analysis, tasks):
    """Create coordination note in orchestrator folder."""
    note_dir = Path(vault_path) / 'notes' / 'orchestrator'
    note_dir.mkdir(parents=True, exist_ok=True)

    ticket_id = ticket['metadata'].get('id', 'unknown')
    note_file = note_dir / f"coord-{ticket_id}.md"

    content = f"""---
ticket: [[{Path(ticket['path']).stem}]]
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: coordinating
agents: {', '.join(analysis['recommended_agents'])}
---

# Coordination: {ticket_id}

## Ticket Summary

**Priority:** {ticket['metadata'].get('priority', 'medium')}
**Type:** {ticket['metadata'].get('type', 'unknown')}
**Complexity:** {analysis['complexity']}

## Analysis

**Recommended Agents:** {', '.join(analysis['recommended_agents'])}
**Estimated Cost:** ${analysis['estimated_cost']:.2f}

## Task Decomposition

Total tasks created: {len(tasks)}

"""

    for i, task in enumerate(tasks, 1):
        content += f"{i}. [[{task['id']}]] ({task['agent']}) - {task['title']}\n"

    content += f"""

## Delegation Strategy

{analysis.get('strategy_notes', 'Tasks assigned based on agent specializations.')}

## Monitoring

**Check Status:** Every 15 minutes
**Tasks Pending:** {len(tasks)}
**Tasks Active:** 0
**Tasks Done:** 0

## Progress Log

### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Ticket analyzed
- {len(tasks)} tasks created and delegated
- Monitoring started
"""

    with open(note_file, 'w') as f:
        f.write(content)

    print(f"  ✓ Created coordination note: {note_file}")


def main():
    parser = argparse.ArgumentParser(description="SuperBeing Orchestrator")
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--ticket', help='Specific ticket to process')

    args = parser.parse_args()

    vault_path = Path(args.vault)
    inbox_path = vault_path / 'tickets' / 'inbox'

    print("🎯 SuperBeing Orchestrator (Claude Code Web)")
    print(f"📁 Vault: {vault_path}")
    print()

    # Find tickets to process
    if args.ticket:
        tickets = [inbox_path / args.ticket]
    else:
        tickets = list(inbox_path.glob('*.md'))

    if not tickets:
        print("📭 No tickets in inbox")
        print()
        print("To create a ticket, use:")
        print(f"  cp {vault_path}/templates/ticket.md {inbox_path}/my-ticket.md")
        print("  # Edit the ticket")
        print("  python3 scripts/orchestrator.py --vault {vault_path}")
        return

    print(f"📬 Found {len(tickets)} ticket(s)")
    print()

    # Process first ticket (one at a time for clarity)
    ticket_path = tickets[0]
    print(f"📝 Processing: {ticket_path.name}")

    ticket = load_ticket(ticket_path)
    if not ticket:
        print(f"  ❌ Failed to parse ticket")
        return

    print(f"  Priority: {ticket['metadata'].get('priority', 'medium')}")
    print(f"  Type: {ticket['metadata'].get('type', 'unknown')}")
    print()

    # Analyze ticket
    print("🔍 Analyzing ticket complexity...")
    analysis = analyze_ticket_complexity(ticket)

    print(f"  Complexity: {analysis['complexity']}")
    print(f"  Recommended agents: {', '.join(analysis['recommended_agents'])}")
    print(f"  Estimated cost: ${analysis['estimated_cost']:.2f}")
    print()

    # THIS IS WHERE CLAUDE WEB (YOU) TAKES OVER
    print("🤖 ORCHESTRATOR (Claude Web): Now it's YOUR turn!")
    print()
    print("I've analyzed the ticket. Your job:")
    print()
    print("1. READ the ticket carefully")
    print("2. DECOMPOSE into specific subtasks")
    print("3. CREATE task notes using create_task_note()")
    print("4. DELEGATE by placing in /tasks/delegated/{agent}/")
    print("5. MONITOR progress in coordination note")
    print()
    print(f"Ticket location: {ticket_path}")
    print()
    print("Example decomposition:")
    print("  tasks = [")
    print("    {")
    print("      'subtask_id': '001',")
    print("      'agent': 'gemini',")
    print("      'title': 'Analyze VideoPlayer.tsx',")
    print("      'objective': 'Identify performance bottlenecks',")
    print("      'estimated_time': '20min',")
    print("      'max_time': '30 minutes',")
    print("      'exit_criteria': '- [ ] List of bottlenecks\\n- [ ] Metrics collected',")
    print("      'files': 'VideoPlayer.tsx',")
    print("      'output_format': 'markdown report',")
    print("      'artifact_dir': 'reports'")
    print("    },")
    print("  ]")
    print()
    print("Then call:")
    print("  for task_data in tasks:")
    print("      create_task_note(vault_path, ticket, task_data)")
    print()
    print("  move_ticket(ticket_path, vault_path, 'active')")
    print("  create_orchestrator_note(vault_path, ticket, analysis, tasks)")


if __name__ == '__main__':
    main()
