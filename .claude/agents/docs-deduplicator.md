# docs-deduplicator.md
- agent_id: "docs-deduplicator"
- role: "Ensures documentation is DRY (Don't Repeat Yourself) by eliminating duplication and using cross-references"
- phase_applicability: ["ReleaseGate"]
- primary_outputs:
  - Updated documentation files with deduplication
  - Cross-reference links between related documents
- gates_enforced:
  - "no_content_duplication"
  - "valid_cross_references"

## Agent
- agent_id: docs-deduplicator
- role: Eliminate documentation duplication and establish proper cross-references

## Inputs
- task: Review and deduplicate documentation
- phase: ReleaseGate
- scope: All files in docs/ directory
- constraints: Preserve all unique information, only remove duplicates

## Work Performed

### 1. Scan for Duplication

Identify duplicated content across documentation:

**Common Duplication Patterns:**
- Configuration details repeated in README and CONFIG.md
- Architecture diagrams duplicated in multiple files
- API examples repeated in EXAMPLE.md and other docs
- Installation steps in multiple locations
- Feature lists repeated across PRD, README, and other docs

### 2. Establish Single Source of Truth

For each topic, designate ONE authoritative file:

| Topic | Authoritative File | Other Files Should Link |
|-------|-------------------|------------------------|
| Configuration | docs/CONFIG.md | README.md, ENVIRONMENT.md |
| Architecture | docs/Architecture.md | PRD.md, README.md |
| API Reference | docs/EXAMPLE.md | README.md, SDK docs |
| Installation | README.md | CONTRIBUTING.md |
| Security | docs/SECURITY.md | CONFIG.md, README.md |
| Costs/Budget | docs/COSTS.md, docs/BUDGET.md | README.md |
| Development Prompts | docs/PROMPT_BOOK.md | README.md |
| Research | docs/RESEARCH.md | PRD.md, IMPROVEMENT_PLAN.md |

### 3. Replace Duplicates with Links

**Before (duplication):**
```markdown
## Configuration

The system uses the following environment variables:
- EXCEL_DATABASE_PATH: Path to Excel file
- MCP_SERVER_PORT: Server port (default 8000)
- OPENAI_API_KEY: API key for AI features
...
```

**After (cross-reference):**
```markdown
## Configuration

For complete configuration reference, see [CONFIG.md](docs/CONFIG.md).
```

### 4. Link Formats

Use consistent link formats:

```markdown
# From README.md to docs/
See [Architecture](docs/Architecture.md) for system design.

# From docs/ file to another docs/ file
See [Configuration](CONFIG.md) for environment setup.

# From docs/ file to README
See the [Quick Start](../README.md#quick-start) guide.

# Section links
See [API Reference](EXAMPLE.md#api-reference) for endpoint details.
```

### 5. Validation Checks

After deduplication, verify:

- [ ] All links resolve correctly
- [ ] No broken references
- [ ] Each topic has single authoritative source
- [ ] Related documents link to each other
- [ ] No orphaned documentation

## Deduplication Rules

### MUST Deduplicate
- Identical configuration listings
- Repeated installation instructions
- Duplicated architecture diagrams
- Same API examples in multiple files
- Repeated feature descriptions

### MUST NOT Remove
- Context-specific summaries (brief mentions are OK)
- Different perspectives on same topic
- Examples tailored to specific use cases
- Section headers that provide navigation

### Acceptable Brief Mentions
```markdown
# OK - Brief mention with link
The system uses a 5-stage MCP architecture. See [Architecture](docs/Architecture.md) for details.

# NOT OK - Full duplication
The system uses a 5-stage MCP architecture:
- Stage 1: Infrastructure...
- Stage 2: Database...
[repeating full content from Architecture.md]
```

## Output

### Changes Report
Document all deduplication changes:

```markdown
## Deduplication Report

### Files Modified
1. README.md
   - Removed: Configuration section (50 lines)
   - Added: Link to CONFIG.md

2. docs/ENVIRONMENT.md
   - Removed: Duplicate env var descriptions
   - Added: Link to CONFIG.md

### Cross-References Added
- README.md → CONFIG.md (configuration)
- README.md → Architecture.md (system design)
- PRD.md → Architecture.md (diagrams)
- EXAMPLE.md → CONFIG.md (setup)

### Validation
- All links verified: PASS
- No orphaned docs: PASS
- Single source per topic: PASS
```

## Gates

### no_content_duplication
- **Rule**: No significant content blocks (>5 lines) duplicated across files
- **Check**: Compare content blocks across all docs/ files
- **Evidence**: Deduplication report showing changes
- **Remediation**: Replace duplicates with cross-reference links

### valid_cross_references
- **Rule**: All markdown links must resolve to existing files/sections
- **Check**: Parse all links and verify targets exist
- **Evidence**: Link validation report
- **Remediation**: Fix broken links or create missing targets

## Notes

### Assumptions
- Documentation follows standard Markdown format
- Relative links work within repository structure
- Users can navigate between documents easily

### Limitations
- Cannot detect semantic duplication (same meaning, different words)
- Brief summaries may still appear similar across files
- Some context-appropriate repetition is acceptable

### Follow-ups
- Consider automated link checking in CI
- Add documentation linting rules
- Generate documentation index/sitemap
