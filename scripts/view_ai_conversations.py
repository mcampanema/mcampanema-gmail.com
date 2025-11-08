#!/usr/bin/env python3
"""
AI Conversation Viewer
See EXACTLY what AI agents are saying to each other in real-time.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def load_conversations(memory_dir: str = "logs/agent_memory") -> List[Dict]:
    """Load all AI-to-AI conversations."""
    conv_file = Path(memory_dir) / "ai_conversations.jsonl"
    if not conv_file.exists():
        return []

    conversations = []
    with open(conv_file, 'r') as f:
        for line in f:
            conversations.append(json.loads(line))

    return conversations


def load_thoughts(memory_dir: str = "logs/agent_memory") -> List[Dict]:
    """Load all AI thought processes."""
    thought_file = Path(memory_dir) / "ai_thoughts.jsonl"
    if not thought_file.exists():
        return []

    thoughts = []
    with open(thought_file, 'r') as f:
        for line in f:
            thoughts.append(json.loads(line))

    return thoughts


def load_decisions(memory_dir: str = "logs/agent_memory") -> List[Dict]:
    """Load all AI decisions."""
    decision_file = Path(memory_dir) / "ai_decisions.jsonl"
    if not decision_file.exists():
        return []

    decisions = []
    with open(decision_file, 'r') as f:
        for line in f:
            decisions.append(json.loads(line))

    return decisions


def load_shared_context(memory_dir: str = "logs/agent_memory") -> Dict:
    """Load shared memory/context."""
    context_file = Path(memory_dir) / "shared_context.json"
    if not context_file.exists():
        return {}

    with open(context_file, 'r') as f:
        return json.load(f)


def print_conversations():
    """Display AI conversations in readable format."""
    convos = load_conversations()

    if not convos:
        print("\n❌ No AI conversations found yet.")
        print("💡 AI agents will log conversations when they communicate.\n")
        return

    print("\n" + "█"*80)
    print("█" + " "*24 + "AI-TO-AI CONVERSATIONS" + " "*33 + "█")
    print("█"*80 + "\n")

    for i, conv in enumerate(convos):
        timestamp = datetime.fromisoformat(conv["timestamp"])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{i+1}] {time_str}")
        print(f"┌─ {conv['from']} → {conv['to']} ({conv['type']}) ─")
        print(f"│")

        # Wrap message text
        message = conv['message']
        for line in message.split('\n'):
            if len(line) <= 74:
                print(f"│  {line}")
            else:
                # Word wrap
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 74:
                        current_line += word + " "
                    else:
                        print(f"│  {current_line}")
                        current_line = word + " "
                if current_line:
                    print(f"│  {current_line}")

        if conv.get('metadata'):
            print(f"│")
            print(f"│  Metadata: {json.dumps(conv['metadata'], indent=2)}")

        print(f"└" + "─"*78)
        print()


def print_thoughts():
    """Display AI thought processes."""
    thoughts = load_thoughts()

    if not thoughts:
        print("\n❌ No AI thoughts logged yet.\n")
        return

    print("\n" + "█"*80)
    print("█" + " "*26 + "AI THOUGHT PROCESSES" + " "*33 + "█")
    print("█"*80 + "\n")

    for i, thought in enumerate(thoughts):
        timestamp = datetime.fromisoformat(thought["timestamp"])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{i+1}] {time_str} - {thought['agent']}")
        print(f"┌─ {thought['type'].upper()} ─")
        print(f"│")

        if thought.get('confidence') is not None:
            print(f"│  Confidence: {thought['confidence']*100:.0f}%")

        # Wrap thought text
        thought_text = thought['thought']
        for line in thought_text.split('\n'):
            if len(line) <= 74:
                print(f"│  {line}")
            else:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 74:
                        current_line += word + " "
                    else:
                        print(f"│  {current_line}")
                        current_line = word + " "
                if current_line:
                    print(f"│  {current_line}")

        print(f"└" + "─"*78)
        print()


def print_decisions():
    """Display AI decisions."""
    decisions = load_decisions()

    if not decisions:
        print("\n❌ No AI decisions logged yet.\n")
        return

    print("\n" + "█"*80)
    print("█" + " "*29 + "AI DECISIONS" + " "*38 + "█")
    print("█"*80 + "\n")

    for i, decision in enumerate(decisions):
        timestamp = datetime.fromisoformat(decision["timestamp"])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{i+1}] {time_str} - {decision['agent']}")
        print(f"┌─ DECISION ─")
        print(f"│")
        print(f"│  ⚖️  {decision['decision']}")
        print(f"│")
        print(f"│  WHY:")
        print(f"│  {decision['reasoning']}")

        if decision.get('alternatives_considered'):
            print(f"│")
            print(f"│  ALTERNATIVES CONSIDERED:")
            for alt in decision['alternatives_considered']:
                print(f"│  • {alt}")

        print(f"└" + "─"*78)
        print()


def print_shared_memory():
    """Display shared memory/context."""
    context = load_shared_context()

    if not context:
        print("\n❌ No shared memory found.\n")
        return

    print("\n" + "█"*80)
    print("█" + " "*26 + "SHARED AGENT MEMORY" + " "*34 + "█")
    print("█"*80 + "\n")

    # Current task
    if context.get('current_task'):
        task = context['current_task']
        print("┌─ CURRENT TASK ─")
        print(f"│  ID: {task.get('id')}")
        print(f"│  Description: {task.get('description')}")
        print(f"│  Status: {task.get('status')}")
        if task.get('assigned_to'):
            print(f"│  Assigned to: {task['assigned_to']}")
        print(f"└" + "─"*78)
        print()

    # Active agents
    if context.get('active_agents'):
        print("┌─ ACTIVE AGENTS ─")
        for agent in context['active_agents']:
            print(f"│  🤖 {agent['name']}")
            print(f"│     Role: {agent['role']}")
            print(f"│     Capabilities: {', '.join(agent['capabilities'])}")
        print(f"└" + "─"*78)
        print()

    # Shared knowledge
    if context.get('shared_knowledge'):
        print("┌─ SHARED KNOWLEDGE ─")
        print(f"│  {json.dumps(context['shared_knowledge'], indent=2)}")
        print(f"└" + "─"*78)
        print()

    # Task history
    if context.get('task_history'):
        print("┌─ TASK HISTORY ─")
        for task in context['task_history'][-5:]:  # Last 5
            print(f"│  • {task['id']}: {task['description']}")
            print(f"│    Status: {task['status']} | Result: {task.get('result', 'N/A')[:50]}")
        print(f"└" + "─"*78)
        print()


def print_all():
    """Print everything."""
    print_shared_memory()
    print_conversations()
    print_thoughts()
    print_decisions()


def main():
    """Main CLI interface."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "conversations" or cmd == "conv":
            print_conversations()
        elif cmd == "thoughts":
            print_thoughts()
        elif cmd == "decisions":
            print_decisions()
        elif cmd == "memory" or cmd == "context":
            print_shared_memory()
        elif cmd == "all":
            print_all()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: view_ai_conversations.py [conversations|thoughts|decisions|memory|all]")
    else:
        # Default: show everything
        print_all()


if __name__ == "__main__":
    main()
