#!/bin/bash
# API Key Audit Script
# Shows EXACTLY which API keys are configured and where.
# NO SECRETS - Just shows which keys exist.

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  API KEY AUDIT - TRANSPARENCY REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Function to check if key exists and show first/last 4 chars
check_key() {
    local key_name=$1
    local key_value="${!key_name}"

    if [ -n "$key_value" ]; then
        local first4="${key_value:0:4}"
        local last4="${key_value: -4}"
        local length=${#key_value}
        echo "✅ $key_name"
        echo "   └─ ${first4}...${last4} (${length} chars)"
        return 0
    else
        echo "❌ $key_name - NOT SET"
        return 1
    fi
}

echo "┌─ ENVIRONMENT VARIABLES ─────────────────────────────────────────────────────┐"
echo "│"

# Check common API keys
check_key "GEMINI_API_KEY"
check_key "API_KEY"
check_key "ANTHROPIC_API_KEY"
check_key "OPENAI_API_KEY"
check_key "GOOGLE_AI_STUDIO_API_KEY"

echo "│"
echo "└──────────────────────────────────────────────────────────────────────────────┘"
echo

# Check .env files
echo "┌─ .ENV FILES ────────────────────────────────────────────────────────────────┐"
echo "│"

if [ -f ".env" ]; then
    echo "📄 .env file found"
    echo "   Keys defined:"
    grep -E "^[A-Z_]+=" .env | sed 's/=.*/=***/' | sed 's/^/   • /'
else
    echo "❌ No .env file found"
fi

if [ -f ".env.local" ]; then
    echo
    echo "📄 .env.local file found"
    echo "   Keys defined:"
    grep -E "^[A-Z_]+=" .env.local | sed 's/=.*/=***/' | sed 's/^/   • /'
else
    echo "❌ No .env.local file found"
fi

echo "│"
echo "└──────────────────────────────────────────────────────────────────────────────┘"
echo

# Check config files
echo "┌─ CONFIG FILES ──────────────────────────────────────────────────────────────┐"
echo "│"

if [ -f "config.json" ]; then
    echo "📄 config.json found"
    if grep -q "apiKey" config.json 2>/dev/null; then
        echo "   ✅ Contains API key references"
    fi
else
    echo "❌ No config.json found"
fi

if [ -f ".claude/settings.json" ]; then
    echo "📄 .claude/settings.json found"
    if grep -q -i "key" .claude/settings.json 2>/dev/null; then
        echo "   ⚠️  Contains 'key' references - review manually"
    fi
fi

echo "│"
echo "└──────────────────────────────────────────────────────────────────────────────┘"
echo

# Check JavaScript/TypeScript files that might have keys hardcoded
echo "┌─ CODE ANALYSIS (Potential hardcoded keys) ──────────────────────────────────┐"
echo "│"

hardcoded_count=$(grep -r "process\.env\." --include="*.js" --include="*.ts" --include="*.tsx" --include="*.html" . 2>/dev/null | grep -v node_modules | wc -l)
if [ "$hardcoded_count" -gt 0 ]; then
    echo "⚠️  Found $hardcoded_count references to process.env in code"
    echo "   Files:"
    grep -r "process\.env\." --include="*.js" --include="*.ts" --include="*.tsx" --include="*.html" . 2>/dev/null | grep -v node_modules | cut -d: -f1 | sort -u | sed 's/^/   • /'
else
    echo "✅ No process.env references found in code"
fi

echo "│"
echo "└──────────────────────────────────────────────────────────────────────────────┘"
echo

# Summary and recommendations
echo "┌─ RECOMMENDATIONS ───────────────────────────────────────────────────────────┐"
echo "│"

if [ -z "$GEMINI_API_KEY" ] && [ -z "$API_KEY" ]; then
    echo "🔴 CRITICAL: No Gemini API key configured!"
    echo "   └─ Set GEMINI_API_KEY or API_KEY environment variable"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "🟡 INFO: No Claude API key configured (using web interface is fine)"
fi

if [ -f ".env" ] && [ ! -f ".gitignore" ]; then
    echo "🔴 WARNING: .env file exists but no .gitignore!"
    echo "   └─ Risk of leaking secrets to git"
elif [ -f ".env" ]; then
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo "✅ .env is properly gitignored"
    else
        echo "🔴 WARNING: .env file NOT in .gitignore!"
    fi
fi

echo "│"
echo "└──────────────────────────────────────────────────────────────────────────────┘"
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  END OF AUDIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "💡 To see AI costs and usage, run:"
echo "   python3 scripts/ai_dashboard.py"
echo
