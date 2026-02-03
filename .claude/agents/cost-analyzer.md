# cost-analyzer.md
- agent_id: "cost-analyzer"
- role: "Tracks actual LLM costs during development and projects hosting costs"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - "docs/COSTS.md"
  - "docs/BUDGET.md"
- gates_enforced:
  - "final_checklist_pass"

## Agent
- agent_id: cost-analyzer
- role: Track actual LLM development costs and project hosting budget.

## Inputs
- task:
- phase:
- scope:
- constraints:

## Work performed
**CRITICAL - Must create TWO files:**

1. **docs/COSTS.md** - Actual LLM costs incurred during development:
   - Read docs/development/PROMPT_LOG.md for Claude usage
   - Calculate actual tokens consumed during development
   - Token costs by phase (PreProject, TaskLoop, ResearchLoop, ReleaseGate)
   - Estimate API costs based on Claude pricing:
     - Claude Opus: $15/1M input, $75/1M output
     - Claude Sonnet: $3/1M input, $15/1M output
   - Include development time (Claude execution time, not human time)
   - Total cost of project built by LLM

2. **docs/BUDGET.md** - Project implementation and hosting budget:
   - **LLM Implementation Cost**: How much it cost to build the project with Claude
     - Tokens consumed
     - API costs at current rates
     - Claude working time (not human time)
   - **Server Hosting Costs**: Production infrastructure
     - MCP server hosting options (VPS, cloud, local)
     - Price comparisons for hosting providers
     - Recommended hosting configurations
   - **Ongoing LLM Costs**: If AI features are used in production
     - Per-query cost estimates
     - Monthly projections by usage tier
   - Budget scenarios: Low/Medium/High usage

**Data sources:**
- Read docs/development/PROMPT_LOG.md for development activity
- Calculate token estimates from conversation length
- Use current Claude API pricing
- Research typical VPS/cloud hosting prices

**Validation:**
- Both files must exist
- Include actual numerical estimates
- Show calculation methodology
- Reference Claude pricing (not generic LLM pricing)

## Changes
- Provide diffs.

## Updated artifacts
- created:
- modified:
- unchanged:

## Gates
- final_checklist_pass: pass/fail
  - evidence:
  - remediation:

## Notes
- assumptions:
- limitations:
- follow-ups:
