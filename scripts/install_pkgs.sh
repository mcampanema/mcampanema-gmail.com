#!/bin/bash
# Claude Code Web Worker - VM Setup Script
# Runs automatically on SessionStart via .claude/settings.json hook

set -e

echo "🚀 Claude Code Web Worker - Initializing VM..."

# Ensure scripts directory exists
mkdir -p scripts

# Install Python dependencies if needed
if command -v python3 &> /dev/null; then
    echo "✓ Python3 detected"

    # Check if required packages are installed
    python3 -c "import json, os, subprocess, datetime" 2>/dev/null || {
        echo "Installing Python dependencies..."
        # No external packages needed for bridge - using stdlib only
    }
else
    echo "⚠ Python3 not found - bridge scripts may not work"
fi

# Verify git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git not found - cannot push results"
    exit 1
fi

# Set git config if not already set
git config user.name >/dev/null 2>&1 || git config user.name "Claude Web Worker"
git config user.email >/dev/null 2>&1 || git config user.email "ccsweb@claude.ai"

# Create artifacts directory
mkdir -p ccsweb_artifacts

echo "✓ VM setup complete - ready to process tasks"
echo "📁 Artifacts will be saved to: ccsweb_artifacts/"
echo "🌿 Results will be pushed to branch: ${CCS_WEB_BRANCH_PREFIX:-ccsweb/}$(date +%s)-<task>"
echo ""
echo "See CLAUDE.md for instructions on how to use this worker."
