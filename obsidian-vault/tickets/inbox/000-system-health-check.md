---
id: 000-system-health-check
created: 2025-01-05 21:00:00
priority: critical
type: security
status: pending
assigned: null
estimated_cost: $0.00
actual_cost: $0.00
agents_used: []
---

# System Health Check & Security Audit

## Description

Computer is extremely slow - takes 30+ minutes to find downloaded files.
CPU usage feels abnormal, possibly compromised.

**User is non-technical** - need step-by-step instructions in plain English.

## Context

**System:** Windows/Mac/Linux (orchestrator will detect)
**Symptoms:**
- Very slow file search (30+ min)
- High CPU usage
- Possible malware/bloatware

**User Skill Level:** Beginner - needs clear, simple instructions

## Acceptance Criteria

- [ ] Malware scan completed and system confirmed clean
- [ ] Startup programs audited and unnecessary ones removed
- [ ] Disk space checked and optimized if needed
- [ ] File search working normally (under 5 seconds)
- [ ] CPU usage normal (under 30% when idle)
- [ ] Security recommendations in plain English
- [ ] Step-by-step maintenance guide created

## Constraints

**Time Limit:** 2 hours max
**Budget Limit:** $0.00 - Use Llama only (free/local)
**Must Use:** Llama for system diagnostics (free)
**Output Format:** Step-by-step guide with screenshots/explanations

## Special Instructions

**CRITICAL:** User is non-technical. Instructions must be:
- Written in plain English (no jargon)
- Step-by-step with numbered lists
- Include what to expect at each step
- Explain WHY each step matters
- Provide screenshots or visual guides where possible

Example good instruction:
"1. Press the Windows key + R on your keyboard (this opens the 'Run' dialog)
2. Type 'msconfig' and press Enter
3. You'll see a window titled 'System Configuration'
4. Click the 'Startup' tab..."

Example bad instruction:
"Run msconfig, disable non-essential startup entries via Task Manager"

## Expected Output

Create: `/artifacts/reports/000-system-health-guide.md`

Must include:
1. **Immediate Actions** (do these right now)
2. **Diagnostic Results** (what we found)
3. **Step-by-Step Fixes** (how to solve each issue)
4. **Preventive Maintenance** (how to avoid this in future)
5. **What to Watch For** (signs of future problems)
