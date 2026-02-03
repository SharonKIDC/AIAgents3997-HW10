# 10 Scenario Simulations

This document details the 10 scenario simulations required by Section 9.5 of the homework.

---

## Scenario 1: External Data Ingestion (Upward Flow)

**Description**: External data input processed and flowing upward through the tree.

**Hebrew**: ינוציח ןותנ תטילק - הלעמל הלוע שעדימ דוביע

**Path**: `M111 → M110 → M100 → M000`

**External Interface**: File I/O (YAML)

**Steps**:
1. M111 (YAML Config leaf) reads external configuration file
2. Data validated and parsed at M111
3. Result propagates up to M110 (Config Handler)
4. M110 aggregates with sibling data from M112 if needed
5. Combined result flows to M100 (Infrastructure Manager)
6. M100 forwards to M000 (Root Orchestrator)
7. Data now available system-wide

**Token Consumption**: ~50-100 tokens

**Code Example**:
```python
# Request sent to root
result = root.process({
    "action": "initialize",
    "config_path": "config/settings.yaml"
})
# Data flows: M000 → M100 → M110 → M111 (read) → M110 → M100 → M000
```

---

## Scenario 2: LLM Reading (Request and Response)

**Description**: Send request to LLM and return response.

**Hebrew**: LLM-ל האירק - הבושת תרזחו ידועיי הלע לא השקב תחילש

**Path**: `M000 → M200 → M210 → M211`

**External Interface**: External API (LLM/MCP)

**Steps**:
1. M000 receives tool call request
2. Routes to M200 (Application Manager)
3. M200 delegates to M210 (Server Handler)
4. M210 calls M211 (MCP Tools leaf)
5. M211 sends request to external LLM API
6. LLM response received at M211
7. Response propagates back: M211 → M210 → M200 → M000

**Token Consumption**: ~100-500 tokens (varies by LLM response)

**Code Example**:
```python
result = root.process({
    "action": "route_request",
    "target": "application",
    "request": {
        "action": "call_tool",
        "tool_name": "tenant_search",
        "params": {"query": "find tenant in unit A101"}
    }
})
```

---

## Scenario 3: Modular Debugging (Coverage/Linter Check)

**Description**: Identify issues in a single node during coverage/linter phase and fix them.

**Hebrew**: ירלודומ גוביד - ונוקיתו דדוב תמוצב יוהיז (Coverage/Linter בלשכ תוקידב)

**Path**: Single node (e.g., `M122`)

**External Interface**: None (internal testing)

**Steps**:
1. Run linter on specific node: `flake8 tree/M122/src/`
2. Identify issues (unused imports, line length, etc.)
3. Fix identified issues in the node's source
4. Run coverage: `pytest tree/M122/tests/ --cov=tree/M122/src`
5. Identify untested paths
6. Add tests for uncovered branches
7. Verify fix: re-run linter and coverage

**Commands**:
```bash
# Step 1: Identify linter issues
python -m flake8 tree/M122/src/ --count

# Step 2: Run coverage
python -m pytest tree/M122/tests/ --cov=tree/M122/src --cov-report=term-missing

# Step 3: Fix and re-verify
python -m flake8 tree/M122/src/ --count  # Should be 0
```

**Token Consumption**: N/A (development activity)

---

## Scenario 4: Hierarchical Aggregation (Leaves to Root)

**Description**: Collect data from multiple leaves spreading upward to root.

**Hebrew**: תיכרריה היצגרגא - שרושל הבחר םילע תסירפמ םינותנ ףוסיא

**Path**: `M110 + M120 → M100 → M000`

**External Interfaces**: Multiple leaf interfaces

**Steps**:
1. M000 requests infrastructure status
2. M100 queries both children (M110, M120)
3. M110 aggregates from M111 (config) and M112 (logs)
4. M120 aggregates from M121 (Excel) and M122 (SQL)
5. M100 merges results from M110 and M120
6. Combined hierarchical result returns to M000
7. Root has full infrastructure view

**Token Consumption**: ~150-300 tokens

**Code Example**:
```python
result = root.process({
    "action": "status"
})
# Returns aggregated status from all 15 nodes
```

**Result Structure**:
```json
{
  "node_id": "M000",
  "children": {
    "M100": {
      "children": {
        "M110": {"M111": {...}, "M112": {...}},
        "M120": {"M121": {...}, "M122": {...}}
      }
    },
    "M200": {...}
  }
}
```

---

## Scenario 5: Configuration Update (Root to Leaves)

**Description**: Configuration change at root propagates downward to all Mini-Projects.

**Hebrew**: היצרוגיפנוק ןוכדע - Projects-Mini-ה לכל הטמל חלחמה שרושב יוניש

**Path**: `M000 → M100/M200 → Level 2 → All Leaves`

**External Interfaces**: None (internal propagation)

**Steps**:
1. M000 receives configuration update request
2. M000 updates its local configuration
3. M000 propagates to M100 (left child)
4. M100 propagates to M110 and M120
5. M110 propagates to M111 and M112
6. M120 propagates to M121 and M122
7. Simultaneously: M000 → M200 → M210/M220 → M211/M212/M221/M222
8. All 15 nodes updated with new configuration

**Token Consumption**: ~100-200 tokens

**Code Example**:
```python
result = root.process({
    "action": "configure",
    "config": {
        "log_level": "DEBUG",
        "timeout": 60,
        "max_retries": 5
    },
    "propagate": True  # Propagate to all children
})
```

**Propagation Order** (BFS):
```
M000 (root)
├── M100, M200 (Level 1)
├── M110, M120, M210, M220 (Level 2)
└── M111, M112, M121, M122, M211, M212, M221, M222 (Level 3)
```

---

## Scenario 6: Error Handling (Failure with Retry)

**Description**: Failure in leaf bubbles up with retry logic through parent.

**Hebrew**: האיגשב לופיט - באה ךרד רזוח בותינו הלעב ןולשכ

**Path**: `M122 → M120 → M100 (retry)`

**External Interface**: Database (error case)

**Steps**:
1. M122 attempts database operation
2. Operation fails (connection timeout, constraint violation)
3. M122 returns error result to M120
4. M120 evaluates error type
5. M120 initiates retry via M122 (up to max_retries)
6. If retry succeeds: return success to M100
7. If all retries fail: propagate error to M100
8. M100 logs error and returns failure status to M000

**Token Consumption**: ~40-100 tokens

**Code Example**:
```python
# Simulated error scenario
result = root.process({
    "action": "route_request",
    "target": "infrastructure",
    "request": {
        "action": "query_db",
        "sql": "SELECT * FROM invalid_table"  # Will fail
    }
})
# Returns: {"success": False, "error": "Table not found", "retries": 3}
```

---

## Scenario 7: Load Balancing (Token Transfer Between Leaves)

**Description**: Transfer tasks between leaves to balance token consumption.

**Hebrew**: םיסמוע ןוזיא - םינקוט תכירצ ןוזיאל םילע ןיב תומישמ תרבעה

**Path**: All leaves via M000 (TokenBalancer)

**External Interfaces**: None (internal operation)

**Steps**:
1. M000 detects unbalanced token usage across leaves
2. TokenBalancer calculates current utilization per leaf
3. Identifies over-utilized leaves (e.g., M211 at 90%)
4. Identifies under-utilized leaves (e.g., M222 at 20%)
5. Recalculates weights based on usage patterns
6. Redistributes token budget across all 8 leaves
7. Notifies affected nodes of new budgets

**Token Consumption**: ~200-500 tokens

**Complexity**: O(n²) for full rebalance

**Code Example**:
```python
result = root.process({
    "action": "rebalance"
})
# Returns new allocations for all leaves:
# {"M111": 5000, "M112": 3000, "M121": 5000, "M122": 8000,
#  "M211": 20000, "M212": 5000, "M221": 8000, "M222": 6000}
```

**Before/After Comparison**:
```
Before Rebalance:        After Rebalance:
M211: 30000 (90% used)   M211: 25000 (72% used)
M222: 3000 (20% used)    M222: 8000 (60% used)
```

---

## Scenario 8: Module Addition (Extending Tree with New Leaf)

**Description**: Extend the tree with a new leaf while preserving structure.

**Hebrew**: לודומ תפסוה - הנבמה תרימש ךות שדח הלעב ץעה תבחרה

**Path**: Parent node (e.g., M220) + New leaf (e.g., M223)

**External Interfaces**: New leaf's interface (e.g., Email)

**Steps**:
1. Identify parent node for new leaf (M220 - Output Handler)
2. Create new leaf node directory structure
3. Implement new leaf (M223 - Email Sender)
4. Update parent (M220) to recognize new child
5. Register new leaf with TokenBalancer
6. Allocate initial token budget to M223
7. Run tests to verify tree integrity
8. Tree now has 16 nodes

**Note**: In our binary tree, adding a leaf requires either:
- Splitting an existing leaf into two children (converting it to internal)
- Adding to a handler that can support dynamic children

**Code Example** (conceptual):
```python
# 1. Create new leaf module
# tree/M223/src/main.py
class EmailSenderNode(LeafNode):
    def __init__(self):
        config = NodeConfig(
            node_id="M223",
            name="Email Sender",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M220"
        )
        super().__init__(config)
        self._interface_type = "email"

# 2. Update parent to include new child
# M220 now coordinates M221, M222, and M223
```

---

## Scenario 9: Results Merging (Combining Outputs)

**Description**: Combine outputs from multiple leaves into unified result.

**Hebrew**: תואצות גוזימ - הדיחא האצותל םילעה המכמ םיטלפ בוליש

**Path**: `M222 + M221 → M220 → M200 → M000`

**External Interfaces**: Multiple (PDF, HTTP)

**Steps**:
1. M000 initiates report generation workflow
2. M220 (Output Handler) receives request
3. M220 calls M222 for PDF generation (parallel)
4. M220 calls M221 for web notification (parallel)
5. M222 returns PDF file path
6. M221 returns HTTP response status
7. M220 merges results into unified response
8. Combined result returns to M000

**Token Consumption**: ~150-250 tokens

**Code Example**:
```python
result = root.process({
    "action": "full_workflow",
    "workflow_type": "report_and_notify",
    "data": {
        "tenant_id": 123,
        "report_type": "monthly",
        "notify": True
    }
})
# Returns merged result:
# {
#   "pdf": {"path": "reports/tenant_123.pdf", "pages": 5},
#   "notification": {"status": 200, "sent": True},
#   "combined_success": True
# }
```

---

## Scenario 10: Integration Testing (Node with Both Children)

**Description**: Run tests on a node together with both its children.

**Hebrew**: היצרגטניא תקידב - וידלי ינש םע תמוצ לע םינחבמ תצרה

**Path**: `M120` with children `M121` and `M122`

**External Interfaces**: Excel file, Database (via children)

**Steps**:
1. Initialize M120 (Database Handler) with both children
2. Verify M121 (Excel Handler) connected correctly
3. Verify M122 (SQL Database) connected correctly
4. Test workflow: read Excel → insert to database
5. Test workflow: query database → export to Excel
6. Test error handling between children
7. Test token budget propagation to children
8. Verify all parent-child communication works

**Test Commands**:
```bash
# Run integration tests for M120 with children
python -m pytest tree/M120/tests/ -v -k "integration"

# Run full subtree tests
python -m pytest tree/M120/tests/ tree/M121/tests/ tree/M122/tests/ -v
```

**Code Example**:
```python
def test_m120_integration_with_children():
    """Test M120 coordinates both M121 and M122 correctly."""
    # Create M120 with real children
    m120 = DatabaseHandlerNode()

    # Test Excel → Database flow
    result = m120.process({
        "action": "import_data",
        "source": {"type": "excel", "path": "data/tenants.xlsx"},
        "target": {"type": "database", "table": "tenants"}
    })
    assert result.success

    # Verify both children were called
    assert m120.left.was_called  # M121 (Excel)
    assert m120.right.was_called  # M122 (Database)
```

---

## Summary Table

| # | Scenario (Hebrew) | Description | Path |
|---|------------------|-------------|------|
| 1 | ינוציח ןותנ תטילק | External data ingestion (upward) | M111→M110→M100→M000 |
| 2 | LLM-ל האירק | LLM request and response | M000→M200→M210→M211 |
| 3 | ירלודומ גוביד | Modular debugging (coverage/linter) | Single node |
| 4 | תיכרריה היצגרגא | Hierarchical aggregation | Leaves→Root |
| 5 | היצרוגיפנוק ןוכדע | Configuration update (downward) | M000→All nodes |
| 6 | האיגשב לופיט | Error handling with retry | M122→M120→retry |
| 7 | םיסמוע ןוזיא | Load balancing (token transfer) | All leaves |
| 8 | לודומ תפסוה | Module addition | Parent + new leaf |
| 9 | תואצות גוזימ | Results merging | Multiple leaves→parent |
| 10 | היצרגטניא תקידב | Integration testing | Node + both children |

---

## Running Simulations

```bash
# Run all 10 scenarios
python scripts/run_scenarios.py

# Run specific scenario
python scripts/run_scenarios.py --scenario 10

# Run with verbose output
python scripts/run_scenarios.py --verbose

# Output includes:
# - Success/failure status for each scenario
# - Token consumption
# - Nodes traversed
# - Execution details
```
