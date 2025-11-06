#!/usr/bin/env python3
"""
Claude Code Web Worker - Bridge Script
Publishes artifacts and pushes results to a ccsweb/* branch.

Usage:
    python3 scripts/bridge_ccsweb.py [task_name] [--artifacts file1 file2 ...]

Example:
    python3 scripts/bridge_ccsweb.py "fix-video-controls" --artifacts out/report.md out/changes.json
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_cmd(cmd, check=True, capture=True):
    """Run shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture,
        text=True,
        check=check
    )
    return result.stdout.strip() if capture else result.returncode


def get_env(key, default=""):
    """Get environment variable with default."""
    return os.environ.get(key, default)


def main():
    # Parse arguments
    task_name = sys.argv[1] if len(sys.argv) > 1 else "task"
    artifacts = []

    if "--artifacts" in sys.argv:
        idx = sys.argv.index("--artifacts")
        artifacts = sys.argv[idx + 1:]

    # Configuration
    branch_prefix = get_env("CCS_WEB_BRANCH_PREFIX", "ccsweb/")
    artifact_dir = get_env("CCS_WEB_ART_DIR", "ccsweb_artifacts")
    timestamp = int(datetime.utcnow().timestamp())
    branch_name = f"{branch_prefix}{timestamp}-{task_name.replace(' ', '-')}"

    print(f"🌉 Claude Code Web Bridge")
    print(f"📝 Task: {task_name}")
    print(f"🌿 Branch: {branch_name}")
    print(f"📦 Artifacts: {len(artifacts)} file(s)")
    print()

    # Create artifact directory
    Path(artifact_dir).mkdir(parents=True, exist_ok=True)

    # Copy artifacts to artifact directory
    for artifact in artifacts:
        if os.path.exists(artifact):
            dest = Path(artifact_dir) / Path(artifact).name
            print(f"  → Copying {artifact} to {dest}")
            run_cmd(f"cp -r '{artifact}' '{dest}'")
        else:
            print(f"  ⚠ Artifact not found: {artifact}")

    # Create manifest
    manifest = {
        "task": task_name,
        "timestamp": timestamp,
        "datetime_utc": datetime.utcnow().isoformat(),
        "branch": branch_name,
        "artifacts": [str(Path(artifact_dir) / Path(a).name) for a in artifacts if os.path.exists(a)],
        "worker": "claude-code-web",
        "repo": run_cmd("git remote get-url origin 2>/dev/null || echo 'unknown'", check=False)
    }

    manifest_path = Path(artifact_dir) / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Manifest written to {manifest_path}")
    print()

    # Git operations
    current_branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    print(f"📍 Current branch: {current_branch}")

    # Stage artifact directory (force add to override .gitignore)
    run_cmd(f"git add -f {artifact_dir}")

    # Check if there are changes to commit
    status = run_cmd("git status --porcelain", check=False)
    if not status:
        print("⚠ No changes to commit - artifact directory may already be committed")
    else:
        # Commit changes
        commit_msg = f"[ccsweb] {task_name}\n\nTimestamp: {timestamp}\nBranch: {branch_name}"
        run_cmd(f"git commit -m '{commit_msg}'")
        print("✓ Changes committed")

    # Create and push new branch
    print(f"🚀 Creating branch {branch_name}...")
    run_cmd(f"git branch {branch_name}")

    print(f"📤 Pushing to origin...")
    push_result = run_cmd(f"git push -u origin {branch_name}", check=False)

    if push_result == 0:
        print(f"✅ Successfully pushed to {branch_name}")
        print()
        print(f"🔗 Your local watcher can now pull artifacts from:")
        print(f"   git fetch origin {branch_name}")
        print(f"   git checkout {branch_name}")
        print(f"   # Artifacts are in {artifact_dir}/")
    else:
        print(f"❌ Failed to push branch - check network/permissions")
        print(f"   You can manually push later with:")
        print(f"   git push -u origin {branch_name}")

    # Return to original branch
    print()
    print(f"↩️  Returning to {current_branch}...")
    run_cmd(f"git checkout {current_branch}")

    print()
    print("✅ Bridge complete!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/bridge_ccsweb.py <task_name> [--artifacts file1 file2 ...]")
        print()
        print("Example:")
        print("  python3 scripts/bridge_ccsweb.py 'fix-video-controls' --artifacts out/report.md out/changes.json")
        sys.exit(1)

    main()
