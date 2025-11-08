#!/usr/bin/env python3
"""
AI Transparency Dashboard
Real-time view of ALL AI operations, costs, and actions.
ZERO BS - Just facts.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


def load_logs(log_dir: str = "logs/ai_transparency") -> List[Dict]:
    """Load all JSONL log entries."""
    log_path = Path(log_dir)
    if not log_path.exists():
        return []

    entries = []
    for log_file in log_path.glob("session_*.jsonl"):
        with open(log_file, 'r') as f:
            for line in f:
                entries.append(json.loads(line))

    return sorted(entries, key=lambda x: x["timestamp"], reverse=True)


def load_summary(log_dir: str = "logs/ai_transparency") -> Dict:
    """Load summary statistics."""
    summary_file = Path(log_dir) / "summary.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            return json.load(f)
    return {
        "total_calls": 0,
        "total_cost_usd": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "by_model": {},
        "by_date": {}
    }


def print_dashboard():
    """Print real-time dashboard."""
    summary = load_summary()
    entries = load_logs()

    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "AI TRANSPARENCY DASHBOARD" + " "*33 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    # Summary
    print("\n┌─ OVERALL STATISTICS " + "─"*57 + "┐")
    print(f"│ Total API Calls:      {summary['total_calls']:>6} calls")
    print(f"│ Total Cost:           ${summary['total_cost_usd']:>9.2f} USD")
    print(f"│ Total Input Tokens:   {summary['total_input_tokens']:>9,}")
    print(f"│ Total Output Tokens:  {summary['total_output_tokens']:>9,}")
    print("└" + "─"*78 + "┘")

    # By Model
    print("\n┌─ COST BY MODEL " + "─"*62 + "┐")
    print("│ Model                      │  Calls │    Cost USD │    Input │   Output │")
    print("├" + "─"*28 + "┼" + "─"*8 + "┼" + "─"*13 + "┼" + "─"*10 + "┼" + "─"*10 + "┤")

    for model, stats in sorted(summary["by_model"].items(), key=lambda x: x[1]["cost_usd"], reverse=True):
        model_short = (model[:25] + "...") if len(model) > 25 else model
        print(f"│ {model_short:26} │ {stats['calls']:6} │ ${stats['cost_usd']:10.4f} │ {stats['input_tokens']:8,} │ {stats['output_tokens']:8,} │")

    print("└" + "─"*78 + "┘")

    # Recent Activity
    print("\n┌─ RECENT ACTIVITY (Last 10 calls) " + "─"*43 + "┐")
    print("│ Time       │ Model              │ Provider   │   Cost   │ Prompt Preview")
    print("├" + "─"*12 + "┼" + "─"*20 + "┼" + "─"*12 + "┼" + "─"*10 + "┼" + "─"*22 + "┤")

    for entry in entries[:10]:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        time_str = timestamp.strftime("%H:%M:%S")
        model_short = (entry["model"][:18] + "..") if len(entry["model"]) > 18 else entry["model"]
        provider_short = entry["provider"][:10]
        cost = entry["cost_usd"]
        preview = entry["prompt_preview"][:20]

        print(f"│ {time_str} │ {model_short:18} │ {provider_short:10} │ ${cost:7.5f} │ {preview:20} │")

    print("└" + "─"*78 + "┘")

    # Daily Costs
    print("\n┌─ DAILY COSTS (Last 7 days) " + "─"*49 + "┐")
    print("│ Date       │  Calls │    Cost USD │")
    print("├" + "─"*12 + "┼" + "─"*8 + "┼" + "─"*13 + "┤")

    for date, stats in sorted(summary["by_date"].items(), reverse=True)[:7]:
        print(f"│ {date:10} │ {stats['calls']:6} │ ${stats['cost_usd']:10.4f} │")

    print("└" + "─"*78 + "┘")

    # Cost Warnings
    total_cost = summary["total_cost_usd"]
    if total_cost > 50:
        print("\n⚠️  WARNING: Total costs exceed $50 USD")
    elif total_cost > 20:
        print("\n⚡ NOTICE: Total costs exceed $20 USD")

    print("\n" + "█"*80)
    print(f"Last Updated: {summary.get('last_updated', 'Never')}")
    print("█"*80 + "\n")


def print_detailed_log(limit: int = 20):
    """Print detailed log with full prompts/responses."""
    entries = load_logs()

    print("\n" + "="*80)
    print("DETAILED AI INTERACTION LOG")
    print("="*80)

    for i, entry in enumerate(entries[:limit]):
        print(f"\n[{i+1}] {entry['timestamp']}")
        print(f"Model: {entry['model']} ({entry['provider']})")
        print(f"Cost: ${entry['cost_usd']:.6f} | Tokens: {entry['input_tokens']} in / {entry['output_tokens']} out")

        if entry.get('metadata'):
            print(f"Metadata: {json.dumps(entry['metadata'], indent=2)}")

        print(f"\n--- PROMPT ---")
        print(entry['full_prompt'][:500] + ("..." if len(entry['full_prompt']) > 500 else ""))

        print(f"\n--- RESPONSE ---")
        print(entry['full_response'][:500] + ("..." if len(entry['full_response']) > 500 else ""))

        print("-"*80)


def export_to_csv(output_file: str = "ai_costs.csv"):
    """Export logs to CSV for analysis."""
    entries = load_logs()

    with open(output_file, 'w') as f:
        f.write("timestamp,model,provider,cost_usd,input_tokens,output_tokens,prompt_preview,response_preview\n")
        for entry in entries:
            f.write(f"{entry['timestamp']},{entry['model']},{entry['provider']},{entry['cost_usd']},{entry['input_tokens']},{entry['output_tokens']},\"{entry['prompt_preview']}\",\"{entry['response_preview']}\"\n")

    print(f"✅ Exported {len(entries)} entries to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "detailed":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            print_detailed_log(limit)
        elif cmd == "export":
            output = sys.argv[2] if len(sys.argv) > 2 else "ai_costs.csv"
            export_to_csv(output)
        else:
            print("Usage: ai_dashboard.py [detailed|export] [args]")
    else:
        print_dashboard()
