#!/usr/bin/env python3
"""
Multi-Agent Shared Memory & Communication Logger
TRANSPARENT AI-to-AI communication tracking.

This shows:
- What AI agents are saying to each other
- Their thought processes
- Shared memory/context
- Decision reasoning

NO HIDDEN CONVERSATIONS.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import threading


class MultiAgentMemory:
    """
    Shared memory system for multiple AI agents.
    All agents can read/write to shared context.
    Everything is logged for transparency.
    """

    def __init__(self, memory_dir: str = "logs/agent_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Conversation log (AI-to-AI communication)
        self.conversation_log = self.memory_dir / "ai_conversations.jsonl"

        # Thought process log (internal reasoning)
        self.thought_log = self.memory_dir / "ai_thoughts.jsonl"

        # Shared context (memory accessible to all agents)
        self.context_file = self.memory_dir / "shared_context.json"

        # Decision log (why agents made certain choices)
        self.decision_log = self.memory_dir / "ai_decisions.jsonl"

        # Initialize shared context
        self.context = self._load_context()
        self.lock = threading.Lock()

    def _load_context(self) -> Dict:
        """Load shared context from disk."""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                return json.load(f)
        return {
            "current_task": None,
            "active_agents": [],
            "task_history": [],
            "shared_knowledge": {},
            "user_preferences": {},
            "last_updated": None
        }

    def _save_context(self):
        """Save shared context to disk."""
        with self.lock:
            self.context["last_updated"] = datetime.now().isoformat()
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2)

    def log_conversation(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        message_type: str = "request",
        metadata: Optional[Dict] = None
    ):
        """
        Log AI-to-AI conversation.

        Args:
            from_agent: Sending agent (e.g., "claude-orchestrator")
            to_agent: Receiving agent (e.g., "gemini-analyst")
            message: The actual message content
            message_type: "request", "response", "delegation", "result"
            metadata: Additional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "type": message_type,
            "message": message,
            "metadata": metadata or {}
        }

        with open(self.conversation_log, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        print(f"\n💬 AI Conversation:")
        print(f"   {from_agent} → {to_agent}")
        print(f"   Type: {message_type}")
        print(f"   Message: {message[:100]}..." if len(message) > 100 else f"   Message: {message}")

    def log_thought(
        self,
        agent: str,
        thought: str,
        thought_type: str = "reasoning",
        confidence: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log an agent's internal thought process.

        Args:
            agent: Agent name (e.g., "claude-orchestrator")
            thought: The thought content
            thought_type: "reasoning", "planning", "analysis", "doubt"
            confidence: Confidence level 0-1 (if applicable)
            metadata: Additional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "type": thought_type,
            "thought": thought,
            "confidence": confidence,
            "metadata": metadata or {}
        }

        with open(self.thought_log, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        print(f"\n🧠 AI Thought ({agent}):")
        print(f"   Type: {thought_type}")
        if confidence is not None:
            print(f"   Confidence: {confidence*100:.0f}%")
        print(f"   Thought: {thought}")

    def log_decision(
        self,
        agent: str,
        decision: str,
        reasoning: str,
        alternatives: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log an agent's decision and reasoning.

        Args:
            agent: Agent making decision
            decision: What was decided
            reasoning: Why this decision was made
            alternatives: What else was considered
            metadata: Additional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "alternatives_considered": alternatives or [],
            "metadata": metadata or {}
        }

        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        print(f"\n⚖️  AI Decision ({agent}):")
        print(f"   Decision: {decision}")
        print(f"   Reasoning: {reasoning}")
        if alternatives:
            print(f"   Alternatives considered: {', '.join(alternatives)}")

    def update_context(self, updates: Dict[str, Any]):
        """
        Update shared context (memory).

        Args:
            updates: Dictionary of updates to merge into context
        """
        with self.lock:
            for key, value in updates.items():
                if key in self.context and isinstance(self.context[key], dict) and isinstance(value, dict):
                    self.context[key].update(value)
                else:
                    self.context[key] = value

            self._save_context()

        print(f"\n📝 Shared Memory Updated:")
        print(f"   Keys: {', '.join(updates.keys())}")

    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Read from shared context.

        Args:
            key: Specific key to read (None = entire context)

        Returns:
            Context value or entire context
        """
        with self.lock:
            if key:
                return self.context.get(key)
            return self.context.copy()

    def register_agent(self, agent_name: str, agent_role: str, capabilities: List[str]):
        """
        Register an agent in the system.

        Args:
            agent_name: Unique agent identifier
            agent_role: Role description
            capabilities: What this agent can do
        """
        agent_info = {
            "name": agent_name,
            "role": agent_role,
            "capabilities": capabilities,
            "registered_at": datetime.now().isoformat()
        }

        with self.lock:
            if "active_agents" not in self.context:
                self.context["active_agents"] = []

            # Remove old entry if exists
            self.context["active_agents"] = [
                a for a in self.context["active_agents"] if a["name"] != agent_name
            ]

            # Add new entry
            self.context["active_agents"].append(agent_info)
            self._save_context()

        print(f"\n🤖 Agent Registered:")
        print(f"   Name: {agent_name}")
        print(f"   Role: {agent_role}")
        print(f"   Capabilities: {', '.join(capabilities)}")

    def get_active_agents(self) -> List[Dict]:
        """Get list of all active agents."""
        return self.get_context("active_agents") or []

    def start_task(self, task_id: str, task_description: str, assigned_to: Optional[str] = None):
        """
        Mark start of a new task.

        Args:
            task_id: Unique task identifier
            task_description: What needs to be done
            assigned_to: Which agent is handling it
        """
        task_info = {
            "id": task_id,
            "description": task_description,
            "assigned_to": assigned_to,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }

        self.update_context({"current_task": task_info})

        print(f"\n🎯 Task Started:")
        print(f"   ID: {task_id}")
        print(f"   Description: {task_description}")
        if assigned_to:
            print(f"   Assigned to: {assigned_to}")

    def complete_task(self, task_id: str, result: str):
        """
        Mark task as complete.

        Args:
            task_id: Task identifier
            result: Outcome/result
        """
        current_task = self.get_context("current_task")
        if current_task and current_task["id"] == task_id:
            current_task["status"] = "completed"
            current_task["completed_at"] = datetime.now().isoformat()
            current_task["result"] = result

            # Move to history
            task_history = self.get_context("task_history") or []
            task_history.append(current_task)

            self.update_context({
                "current_task": None,
                "task_history": task_history
            })

            print(f"\n✅ Task Completed:")
            print(f"   ID: {task_id}")
            print(f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}")


# Global memory instance
_memory = None

def get_memory() -> MultiAgentMemory:
    """Get or create global memory instance."""
    global _memory
    if _memory is None:
        _memory = MultiAgentMemory()
    return _memory


# Convenience functions
def ai_says(from_agent: str, to_agent: str, message: str, message_type: str = "request"):
    """Quick conversation log."""
    memory = get_memory()
    memory.log_conversation(from_agent, to_agent, message, message_type)


def ai_thinks(agent: str, thought: str, thought_type: str = "reasoning", confidence: float = None):
    """Quick thought log."""
    memory = get_memory()
    memory.log_thought(agent, thought, thought_type, confidence)


def ai_decides(agent: str, decision: str, reasoning: str, alternatives: List[str] = None):
    """Quick decision log."""
    memory = get_memory()
    memory.log_decision(agent, decision, reasoning, alternatives)


if __name__ == "__main__":
    # Demo: Multi-agent conversation
    memory = MultiAgentMemory()

    # Register agents
    memory.register_agent(
        "claude-orchestrator",
        "Orchestrator & Project Manager",
        ["task_decomposition", "agent_delegation", "progress_monitoring"]
    )

    memory.register_agent(
        "gemini-analyst",
        "Video & Image Analyst",
        ["video_analysis", "image_recognition", "cheap_processing"]
    )

    memory.register_agent(
        "llama-local",
        "Local Processing Agent",
        ["offline_processing", "code_generation", "free_compute"]
    )

    # Start a task
    memory.start_task(
        "task-001",
        "Analyze video for anomalies",
        assigned_to="claude-orchestrator"
    )

    # Claude thinks about the task
    ai_thinks(
        "claude-orchestrator",
        "This video analysis task is suitable for Gemini due to low cost and vision capabilities. Will delegate.",
        thought_type="planning",
        confidence=0.9
    )

    # Claude makes a decision
    ai_decides(
        "claude-orchestrator",
        "Delegate to Gemini Flash for initial analysis",
        "Gemini has best cost/performance for video analysis. Claude Sonnet would cost 40x more.",
        alternatives=["Claude Sonnet (too expensive)", "Llama (no vision API)", "Manual analysis"]
    )

    # Claude talks to Gemini
    ai_says(
        "claude-orchestrator",
        "gemini-analyst",
        "Please analyze this video for anomalies. Focus on detecting unusual patterns in the first 30 seconds.",
        message_type="delegation"
    )

    # Gemini responds
    ai_says(
        "gemini-analyst",
        "claude-orchestrator",
        "Analysis complete. Found 3 anomalies at timestamps 0:15, 0:22, 0:28. Details in attached report.",
        message_type="result"
    )

    # Update shared memory
    memory.update_context({
        "shared_knowledge": {
            "video_001_anomalies": [
                {"timestamp": "0:15", "type": "motion_spike"},
                {"timestamp": "0:22", "type": "color_shift"},
                {"timestamp": "0:28", "type": "audio_glitch"}
            ]
        }
    })

    # Complete task
    memory.complete_task(
        "task-001",
        "Found 3 anomalies. Report generated."
    )

    print("\n" + "="*80)
    print("Check logs/agent_memory/ for full conversation history!")
    print("="*80)
