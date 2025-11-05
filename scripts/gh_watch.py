#!/usr/bin/env python3
"""
Claude Code Web Worker - Local Watcher
Monitors for ccsweb/* branches and pulls artifacts to local out/ directory.

This script runs on YOUR LOCAL MACHINE (not in the web worker VM).

Usage:
    python3 scripts/gh_watch.py [--interval SECONDS] [--out-dir DIR] [--obsidian-vault DIR]

Example:
    python3 scripts/gh_watch.py --interval 30 --out-dir ./out/ccsweb --obsidian-vault ~/Obsidian/SuperBeing
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def run_cmd(cmd, check=True):
    """Run shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def fetch_remote_branches(prefix="ccsweb/"):
    """Fetch and return list of remote ccsweb branches."""
    run_cmd("git fetch origin --prune", check=False)
    output = run_cmd(f"git branch -r | grep 'origin/{prefix}'", check=False)
    branches = [line.strip().replace("origin/", "") for line in output.split("\n") if line.strip()]
    return branches


def get_processed_branches(state_file):
    """Load list of already processed branches."""
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return []


def mark_branch_processed(state_file, branch_name):
    """Mark a branch as processed."""
    processed = get_processed_branches(state_file)
    if branch_name not in processed:
        processed.append(branch_name)
        with open(state_file, "w") as f:
            json.dump(processed, f, indent=2)


def process_branch(branch_name, out_dir, obsidian_vault=None):
    """Process artifacts from a ccsweb branch."""
    print(f"\n🔍 Processing branch: {branch_name}")

    # Checkout the branch
    current_branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    run_cmd(f"git checkout {branch_name}")

    # Find artifact directory
    artifact_dir = "ccsweb_artifacts"
    if not os.path.exists(artifact_dir):
        print(f"  ⚠ No artifact directory found in {branch_name}")
        run_cmd(f"git checkout {current_branch}")
        return False

    # Read manifest
    manifest_path = Path(artifact_dir) / "manifest.json"
    if not manifest_path.exists():
        print(f"  ⚠ No manifest.json found")
        run_cmd(f"git checkout {current_branch}")
        return False

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    print(f"  📝 Task: {manifest.get('task', 'unknown')}")
    print(f"  📅 Date: {manifest.get('datetime_utc', 'unknown')}")
    print(f"  📦 Artifacts: {len(manifest.get('artifacts', []))}")

    # Create output directory with timestamp
    timestamp = manifest.get('timestamp', int(time.time()))
    task_slug = manifest.get('task', 'unknown').replace(' ', '-')
    dest_dir = Path(out_dir) / f"{timestamp}-{task_slug}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy artifacts
    for artifact in manifest.get('artifacts', []):
        if os.path.exists(artifact):
            dest = dest_dir / Path(artifact).name
            print(f"  → Copying {artifact} to {dest}")
            run_cmd(f"cp -r '{artifact}' '{dest}'")

    # Copy manifest
    run_cmd(f"cp '{manifest_path}' '{dest_dir}/manifest.json'")

    print(f"  ✓ Artifacts saved to {dest_dir}")

    # Copy to Obsidian if specified
    if obsidian_vault and os.path.exists(obsidian_vault):
        obsidian_dest = Path(obsidian_vault) / "ccsweb" / f"{timestamp}-{task_slug}"
        obsidian_dest.mkdir(parents=True, exist_ok=True)

        # Copy markdown files to Obsidian
        for artifact in manifest.get('artifacts', []):
            if artifact.endswith('.md') and os.path.exists(artifact):
                dest = obsidian_dest / Path(artifact).name
                print(f"  📓 Copying {artifact} to Obsidian: {dest}")
                run_cmd(f"cp '{artifact}' '{dest}'")

        # Create index note
        index_note = obsidian_dest / "index.md"
        with open(index_note, "w") as f:
            f.write(f"# {manifest.get('task', 'Task')}\n\n")
            f.write(f"**Date:** {manifest.get('datetime_utc', 'unknown')}\n")
            f.write(f"**Branch:** {branch_name}\n")
            f.write(f"**Worker:** {manifest.get('worker', 'unknown')}\n\n")
            f.write("## Artifacts\n\n")
            for artifact in manifest.get('artifacts', []):
                f.write(f"- [[{Path(artifact).name}]]\n")

        print(f"  ✓ Obsidian notes created in {obsidian_dest}")

    # Return to original branch
    run_cmd(f"git checkout {current_branch}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Claude Code Web Worker - Local Watcher")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("--out-dir", default="./out/ccsweb", help="Output directory for artifacts")
    parser.add_argument("--obsidian-vault", help="Path to Obsidian vault (optional)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (no loop)")
    parser.add_argument("--prefix", default="ccsweb/", help="Branch prefix to watch")

    args = parser.parse_args()

    # Create output directory
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    # State file to track processed branches
    state_file = Path(args.out_dir) / ".processed_branches.json"

    print("👁️  Claude Code Web Worker - Local Watcher")
    print(f"📁 Output directory: {args.out_dir}")
    print(f"🌿 Watching for branches: {args.prefix}*")
    if args.obsidian_vault:
        print(f"📓 Obsidian vault: {args.obsidian_vault}")
    print(f"⏱️  Check interval: {args.interval}s")
    print()

    iteration = 0
    while True:
        iteration += 1
        print(f"🔄 Check #{iteration} at {datetime.now().strftime('%H:%M:%S')}")

        # Get remote branches
        branches = fetch_remote_branches(args.prefix)
        processed = get_processed_branches(state_file)

        # Find new branches
        new_branches = [b for b in branches if b not in processed]

        if new_branches:
            print(f"✨ Found {len(new_branches)} new branch(es)")
            for branch in new_branches:
                if process_branch(branch, args.out_dir, args.obsidian_vault):
                    mark_branch_processed(state_file, branch)
        else:
            print("  No new branches")

        if args.once:
            print("\n✓ Single run complete")
            break

        print(f"💤 Sleeping for {args.interval}s...\n")
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Watcher stopped")
        sys.exit(0)
