#!/usr/bin/env python3
"""
Claude Code Web Worker - Automatic Ticket Processor
Processes tasks from tickets/inbox/*.json automatically.

This script is meant to be invoked BY CLAUDE inside the web worker VM
to automatically detect and process queued tasks.

Ticket format (JSON):
{
  "id": "unique-id",
  "type": "task|question|implementation",
  "title": "Short description",
  "description": "Detailed task description",
  "context": {
    "files": ["path/to/file1.ts", "path/to/file2.ts"],
    "relevant_docs": ["https://..."]
  },
  "priority": "high|medium|low",
  "artifacts": ["report.md", "changes.json"]
}

Usage (Claude should run this):
    python3 scripts/ccsweb_worker.py
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime


def load_tickets(inbox_dir="tickets/inbox"):
    """Load all tickets from inbox directory."""
    inbox = Path(inbox_dir)
    if not inbox.exists():
        return []

    tickets = []
    for ticket_file in inbox.glob("*.json"):
        try:
            with open(ticket_file, "r") as f:
                ticket = json.load(f)
                ticket["_file"] = str(ticket_file)
                tickets.append(ticket)
        except Exception as e:
            print(f"⚠ Error loading {ticket_file}: {e}")

    # Sort by priority (high -> medium -> low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tickets.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 1))

    return tickets


def move_ticket(ticket_file, dest_dir):
    """Move ticket to processed/failed directory."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    dest_file = dest / Path(ticket_file).name
    os.rename(ticket_file, dest_file)
    return dest_file


def format_ticket_for_claude(ticket):
    """Format ticket as instructions for Claude."""
    output = f"# Task: {ticket.get('title', 'Untitled')}\n\n"
    output += f"**Type:** {ticket.get('type', 'task')}\n"
    output += f"**Priority:** {ticket.get('priority', 'medium')}\n"
    output += f"**ID:** {ticket.get('id', 'unknown')}\n\n"

    output += "## Description\n\n"
    output += ticket.get('description', 'No description provided') + "\n\n"

    # Context
    context = ticket.get('context', {})
    if context:
        output += "## Context\n\n"

        files = context.get('files', [])
        if files:
            output += "**Relevant files:**\n"
            for f in files:
                output += f"- `{f}`\n"
            output += "\n"

        docs = context.get('relevant_docs', [])
        if docs:
            output += "**Documentation:**\n"
            for d in docs:
                output += f"- {d}\n"
            output += "\n"

    # Expected artifacts
    artifacts = ticket.get('artifacts', [])
    if artifacts:
        output += "## Expected Artifacts\n\n"
        output += "When you complete this task, use the bridge to publish these artifacts:\n"
        for a in artifacts:
            output += f"- `{a}`\n"
        output += "\n"

    output += "## Publishing Results\n\n"
    output += "When done, run:\n"
    output += f"```bash\n"
    output += f"python3 scripts/bridge_ccsweb.py '{ticket.get('id', 'task')}' --artifacts "
    output += " ".join(artifacts if artifacts else ["output.md"])
    output += "\n```\n"

    return output


def main():
    print("🎫 Claude Code Web Worker - Ticket Processor")
    print()

    # Load tickets
    tickets = load_tickets()

    if not tickets:
        print("📭 No tickets in inbox")
        print()
        print("To queue a task, create a JSON file in tickets/inbox/")
        print("Example: tickets/inbox/001-fix-bug.json")
        return

    print(f"📬 Found {len(tickets)} ticket(s)")
    print()

    # Process first ticket (Claude should handle one at a time)
    ticket = tickets[0]
    ticket_file = ticket["_file"]

    print(f"📝 Processing ticket: {ticket.get('title', 'Untitled')}")
    print(f"   File: {ticket_file}")
    print(f"   Priority: {ticket.get('priority', 'medium')}")
    print()

    # Format ticket instructions for Claude
    instructions = format_ticket_for_claude(ticket)

    # Save formatted instructions to current working directory
    instructions_file = "CURRENT_TASK.md"
    with open(instructions_file, "w") as f:
        f.write(instructions)

    print(f"✓ Task instructions written to: {instructions_file}")
    print()
    print("=" * 60)
    print(instructions)
    print("=" * 60)
    print()

    # Move ticket to processing directory
    processing_file = move_ticket(ticket_file, "tickets/processing")
    print(f"📁 Ticket moved to: {processing_file}")
    print()

    print("🤖 CLAUDE: Please read CURRENT_TASK.md and complete the task.")
    print("   When done, run the bridge command shown in the instructions.")
    print()
    print("   After publishing, move the ticket from processing/ to done/:")
    print(f"   mv '{processing_file}' tickets/done/")


if __name__ == "__main__":
    main()
