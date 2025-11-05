#!/usr/bin/env python3
"""
SuperBeing Obsidian Bridge

Syncs between git repo (Claude Web worker) and Obsidian vault.

This replaces the original bridge_ccsweb.py for Obsidian-native workflows.

Usage:
    # Push completed work from Claude Web to Obsidian vault
    python3 scripts/bridge_obsidian.py push --vault /path/to/vault --artifacts report.md

    # Pull new tickets from Obsidian to start work
    python3 scripts/bridge_obsidian.py pull --vault /path/to/vault
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import shutil


def run_cmd(cmd, check=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
    return result.stdout.strip() if result.returncode == 0 else ""


def push_to_obsidian(vault_path, artifacts, notes=None):
    """
    Push completed work from Claude Web back to Obsidian vault.

    This:
    1. Copies artifacts to vault/artifacts/
    2. Creates completion notes
    3. Commits to git
    4. Pushes to remote
    """
    vault = Path(vault_path)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("📤 Pushing to Obsidian vault...")
    print()

    # Copy artifacts
    for artifact in artifacts:
        if os.path.exists(artifact):
            # Determine artifact type from path or extension
            artifact_path = Path(artifact)

            if artifact_path.suffix == '.md':
                dest_dir = vault / 'artifacts' / 'reports'
            elif artifact_path.suffix in ['.ts', '.tsx', '.js', '.py', '.go']:
                dest_dir = vault / 'artifacts' / 'code'
            else:
                dest_dir = vault / 'artifacts'

            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / artifact_path.name

            print(f"  → {artifact} → {dest}")
            shutil.copy2(artifact, dest)

    # Create completion manifest
    manifest = {
        'timestamp': timestamp,
        'worker': 'claude-code-web',
        'artifacts': [str(a) for a in artifacts],
        'notes': notes or []
    }

    manifest_path = vault / 'artifacts' / f"push-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"  ✓ Manifest: {manifest_path}")
    print()

    # Git commit and push
    print("📝 Committing to vault...")
    os.chdir(vault)

    run_cmd("git add artifacts/")

    commit_msg = f"[claude-web] Push artifacts - {timestamp}"
    run_cmd(f"git commit -m '{commit_msg}'")

    current_branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    print(f"  ✓ Committed to {current_branch}")

    print("📤 Pushing to remote...")
    run_cmd(f"git push -u origin {current_branch}")

    print()
    print("✅ Push complete! Orchestrator will see updates on next sync.")


def pull_from_obsidian(vault_path):
    """
    Pull new tickets/tasks from Obsidian vault to Claude Web worker.

    This:
    1. Fetches latest from git
    2. Copies tickets to local workspace
    3. Returns list of tickets to process
    """
    vault = Path(vault_path)

    print("📥 Pulling from Obsidian vault...")
    print()

    # Git pull
    os.chdir(vault)
    current_branch = run_cmd("git rev-parse --abbrev-ref HEAD")

    print(f"  Fetching {current_branch}...")
    run_cmd("git fetch origin")
    run_cmd(f"git pull origin {current_branch}")

    # Find new tickets
    inbox = vault / 'tickets' / 'inbox'
    tickets = list(inbox.glob('*.md')) if inbox.exists() else []

    print()
    if tickets:
        print(f"📬 Found {len(tickets)} ticket(s):")
        for ticket in tickets:
            print(f"  - {ticket.name}")
    else:
        print("📭 No new tickets")

    print()
    return tickets


def main():
    parser = argparse.ArgumentParser(description="SuperBeing Obsidian Bridge")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Push command
    push_parser = subparsers.add_parser('push', help='Push artifacts to Obsidian vault')
    push_parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    push_parser.add_argument('--artifacts', nargs='+', required=True, help='Artifact files to push')
    push_parser.add_argument('--notes', nargs='+', help='Additional note files')

    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull tickets from Obsidian vault')
    pull_parser.add_argument('--vault', required=True, help='Path to Obsidian vault')

    args = parser.parse_args()

    if args.command == 'push':
        push_to_obsidian(args.vault, args.artifacts, args.notes)
    elif args.command == 'pull':
        tickets = pull_from_obsidian(args.vault)
        if tickets:
            print("Next: Process tickets with orchestrator:")
            print(f"  python3 scripts/orchestrator.py --vault {args.vault}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
