#!/usr/bin/env python3
"""
AI Transparency Logger
Logs ALL AI interactions with costs, tokens, and actual communications.
No BS, just facts.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib


class AITransparencyLogger:
    """
    Logs every AI interaction with full transparency.
    Cost tracking, token counting, and complete audit trail.
    """

    # Cost per 1M tokens (as of 2024-11)
    PRICING = {
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # per 1M tokens
        "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-opus-4": {"input": 15.00, "output": 75.00},
        "claude-haiku-3-5": {"input": 1.00, "output": 5.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "kimi-k2": {"input": 0.30, "output": 1.20},  # Estimated
        "llama-3.1-70b": {"input": 0.00, "output": 0.00},  # Local
    }

    def __init__(self, log_dir: str = "logs/ai_transparency"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = f"session_{int(time.time())}"
        self.session_file = self.log_dir / f"{self.session_id}.jsonl"
        self.summary_file = self.log_dir / "summary.json"

        # Load or initialize summary
        self.summary = self._load_summary()

    def _load_summary(self) -> Dict:
        """Load existing summary or create new one."""
        if self.summary_file.exists():
            with open(self.summary_file, 'r') as f:
                return json.load(f)
        return {
            "total_calls": 0,
            "total_cost_usd": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "by_model": {},
            "by_date": {},
            "last_updated": None
        }

    def _save_summary(self):
        """Save summary to disk."""
        self.summary["last_updated"] = datetime.now().isoformat()
        with open(self.summary_file, 'w') as f:
            json.dump(self.summary, f, indent=2)

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD."""
        if model not in self.PRICING:
            print(f"⚠️  Warning: Unknown model '{model}', cannot estimate cost")
            return 0.0

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def log_interaction(
        self,
        model: str,
        provider: str,
        prompt: str,
        response: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a single AI interaction with full transparency.

        Args:
            model: Model name (e.g., "gemini-2.5-flash")
            provider: Provider name (e.g., "google", "anthropic")
            prompt: The actual prompt sent
            response: The actual response received
            input_tokens: Number of input tokens (optional, will estimate if None)
            output_tokens: Number of output tokens (optional, will estimate if None)
            metadata: Additional context (ticket_id, task_name, etc.)

        Returns:
            Log entry dictionary
        """
        # Estimate tokens if not provided (rough estimate: 1 token ≈ 4 chars)
        if input_tokens is None:
            input_tokens = len(prompt) // 4
        if output_tokens is None:
            output_tokens = len(response) // 4

        cost = self._estimate_cost(model, input_tokens, output_tokens)

        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "model": model,
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
            "prompt_preview": prompt[:200] + ("..." if len(prompt) > 200 else ""),
            "response_preview": response[:200] + ("..." if len(response) > 200 else ""),
            "full_prompt": prompt,
            "full_response": response,
            "metadata": metadata or {}
        }

        # Append to session log
        with open(self.session_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        # Update summary
        today = datetime.now().strftime("%Y-%m-%d")
        self.summary["total_calls"] += 1
        self.summary["total_cost_usd"] += cost
        self.summary["total_input_tokens"] += input_tokens
        self.summary["total_output_tokens"] += output_tokens

        # By model
        if model not in self.summary["by_model"]:
            self.summary["by_model"][model] = {
                "calls": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0
            }
        self.summary["by_model"][model]["calls"] += 1
        self.summary["by_model"][model]["cost_usd"] += cost
        self.summary["by_model"][model]["input_tokens"] += input_tokens
        self.summary["by_model"][model]["output_tokens"] += output_tokens

        # By date
        if today not in self.summary["by_date"]:
            self.summary["by_date"][today] = {
                "calls": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0
            }
        self.summary["by_date"][today]["calls"] += 1
        self.summary["by_date"][today]["cost_usd"] += cost
        self.summary["by_date"][today]["input_tokens"] += input_tokens
        self.summary["by_date"][today]["output_tokens"] += output_tokens

        self._save_summary()

        # Print to console
        print(f"🤖 AI Call Logged: {provider}/{model}")
        print(f"   💰 Cost: ${cost:.6f} | 📊 Tokens: {input_tokens} in / {output_tokens} out")

        return entry

    def get_summary(self, by: str = "all") -> Dict:
        """
        Get summary statistics.

        Args:
            by: "all", "model", "date"
        """
        if by == "all":
            return self.summary
        elif by == "model":
            return self.summary["by_model"]
        elif by == "date":
            return self.summary["by_date"]
        else:
            raise ValueError(f"Unknown summary type: {by}")

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "="*60)
        print("AI TRANSPARENCY REPORT")
        print("="*60)
        print(f"Total API Calls: {self.summary['total_calls']}")
        print(f"Total Cost: ${self.summary['total_cost_usd']:.2f} USD")
        print(f"Total Tokens: {self.summary['total_input_tokens']:,} in / {self.summary['total_output_tokens']:,} out")
        print(f"Last Updated: {self.summary['last_updated']}")

        print("\n" + "-"*60)
        print("BY MODEL:")
        print("-"*60)
        for model, stats in sorted(self.summary["by_model"].items(), key=lambda x: x[1]["cost_usd"], reverse=True):
            print(f"{model:25} | Calls: {stats['calls']:4} | Cost: ${stats['cost_usd']:8.4f}")

        print("\n" + "-"*60)
        print("BY DATE:")
        print("-"*60)
        for date, stats in sorted(self.summary["by_date"].items(), reverse=True)[:7]:
            print(f"{date} | Calls: {stats['calls']:4} | Cost: ${stats['cost_usd']:8.4f}")

        print("="*60 + "\n")


# Global logger instance
_logger = None

def get_logger() -> AITransparencyLogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = AITransparencyLogger()
    return _logger


# Convenience function
def log_ai_call(model: str, provider: str, prompt: str, response: str, **kwargs):
    """Quick logging function."""
    logger = get_logger()
    return logger.log_interaction(model, provider, prompt, response, **kwargs)


if __name__ == "__main__":
    # Demo/Test
    logger = AITransparencyLogger()

    # Example usage
    logger.log_interaction(
        model="gemini-2.5-flash",
        provider="google",
        prompt="Analyze this video for anomalies",
        response="I detected 3 anomalies at timestamps...",
        input_tokens=1500,
        output_tokens=800,
        metadata={"ticket_id": "example-001", "task": "video-analysis"}
    )

    logger.log_interaction(
        model="claude-sonnet-4-5",
        provider="anthropic",
        prompt="Orchestrate this multi-step task",
        response="I will break this down into 5 subtasks...",
        input_tokens=5000,
        output_tokens=2000,
        metadata={"role": "orchestrator"}
    )

    logger.print_summary()
