# 10 Scenario Simulations

This document details the 10 scenario simulations required by Section 9.5 of the homework.

---

## Scenario 1: Config Load

**Description**: Load YAML configuration file and propagate upward through the tree.

**Path**: `M111 → M110 → M100 → M000`

**External Interface**: File I/O (YAML)

**Token Consumption**: ~120 tokens

**Steps**:
1. M000 receives configuration request
2. Routes to M100 (Infrastructure Manager)
3. M100 delegates to M110 (Config Handler)
4. M110 calls M111 (YAML Config leaf)
5. M111 reads external YAML file
6. Data validated and parsed at M111
7. Result propagates: M111 → M110 → M100 → M000

**Code Example**:
```python
result = root.process({
    "action": "load_config",
    "config_path": "config/settings.yaml"
})
```

---

## Scenario 2: Tenant Query

**Description**: Query tenant information from the database.

**Path**: `M122 → M120 → M100 → M000`

**External Interface**: SQLite/PostgreSQL Database

**Token Consumption**: ~180 tokens

**Steps**:
1. M000 receives tenant query request
2. Routes to M100 (Infrastructure Manager)
3. M100 delegates to M120 (Database Handler)
4. M120 calls M122 (SQL Database leaf)
5. M122 executes SQL query against database
6. Result propagates: M122 → M120 → M100 → M000

**Code Example**:
```python
result = root.process({
    "action": "query_tenant",
    "tenant_id": 123
})
```

---

## Scenario 3: Excel Import

**Description**: Import tenant data from an Excel file.

**Path**: `M121 → M120 → M100 → M000`

**External Interface**: File I/O (Excel)

**Token Consumption**: ~150 tokens

**Steps**:
1. M000 receives import request
2. Routes to M100 (Infrastructure Manager)
3. M100 delegates to M120 (Database Handler)
4. M120 calls M121 (Excel Handler leaf)
5. M121 reads and parses Excel file
6. Result propagates: M121 → M120 → M100 → M000

**Code Example**:
```python
result = root.process({
    "action": "import_excel",
    "file_path": "data/tenants.xlsx"
})
```

---

## Scenario 4: MCP Tool Call

**Description**: Call external LLM tool via MCP interface.

**Path**: `M000 → M200 → M210 → M211`

**External Interface**: External API (LLM/MCP)

**Token Consumption**: ~200 tokens

**Steps**:
1. M000 receives tool call request
2. Routes to M200 (Application Manager)
3. M200 delegates to M210 (Server Handler)
4. M210 calls M211 (MCP Tools leaf)
5. M211 sends request to external LLM API
6. Response propagates: M211 → M210 → M200 → M000

**Code Example**:
```python
result = root.process({
    "action": "call_tool",
    "tool_name": "tenant_search",
    "params": {"query": "find tenant in unit A101"}
})
```

---

## Scenario 5: PDF Generation

**Description**: Generate a PDF report for a tenant.

**Path**: `M000 → M200 → M220 → M222`

**External Interface**: File I/O (PDF)

**Token Consumption**: ~160 tokens

**Steps**:
1. M000 receives PDF generation request
2. Routes to M200 (Application Manager)
3. M200 delegates to M220 (Output Handler)
4. M220 calls M222 (PDF Generator leaf)
5. M222 generates and writes PDF file
6. Result propagates: M222 → M220 → M200 → M000

**Code Example**:
```python
result = root.process({
    "action": "generate_pdf",
    "tenant_id": 123,
    "report_type": "monthly"
})
```

---

## Scenario 6: Web API Request

**Description**: Handle incoming REST API request.

**Path**: `M221 → M220 → M200 → M000`

**External Interface**: HTTP (REST API)

**Token Consumption**: ~140 tokens

**Steps**:
1. M221 (Web Interface leaf) receives HTTP request
2. Request validated at M221
3. Propagates to M220 (Output Handler)
4. M220 forwards to M200 (Application Manager)
5. M200 forwards to M000 (Root Orchestrator)
6. Response flows back down the same path

**Code Example**:
```python
# Incoming request at M221
request = {
    "method": "GET",
    "path": "/api/tenants/123",
    "headers": {"Authorization": "Bearer ..."}
}
result = m221.handle_request(request)
```

---

## Scenario 7: Hierarchical Merge

**Description**: Merge configuration and database data at parent level.

**Path**: `M110 + M120 → M100`

**External Interfaces**: YAML (via M111), Database (via M122)

**Token Consumption**: ~130 tokens

**Steps**:
1. M100 requests data from both children
2. M110 aggregates from M111 (config) and M112 (logs)
3. M120 aggregates from M121 (Excel) and M122 (SQL)
4. M100 receives results from both M110 and M120
5. M100 merges into unified infrastructure view
6. Combined result returns to M000

**Code Example**:
```python
result = root.process({
    "action": "get_infrastructure_status"
})
# Returns merged data from config + database
```

---

## Scenario 8: Error Propagation

**Description**: Handle database error with retry logic.

**Path**: `M122 → M120 → M100 (retry)`

**External Interface**: Database (error case)

**Token Consumption**: ~90 tokens

**Steps**:
1. M122 attempts database operation
2. Operation fails (connection timeout)
3. M122 returns error to M120
4. M120 evaluates error type
5. M120 initiates retry via M122 (up to max_retries)
6. If retry succeeds: return success
7. If all retries fail: propagate error to M100

**Code Example**:
```python
result = root.process({
    "action": "query_db",
    "sql": "SELECT * FROM tenants WHERE id = 999"
})
# On failure: {"success": False, "error": "...", "retries": 3}
```

---

## Scenario 9: Load Rebalancing

**Description**: Redistribute token budget across all leaves.

**Path**: `M000 → all leaves` (via TokenBalancer)

**External Interfaces**: None (internal operation)

**Token Consumption**: ~80 tokens

**Complexity**: O(n²) for full rebalance

**Steps**:
1. M000 detects unbalanced token usage
2. TokenBalancer calculates current utilization
3. Identifies over/under-utilized leaves
4. Recalculates weights based on usage
5. Redistributes budget across all 8 leaves
6. Notifies affected nodes

**Code Example**:
```python
result = root.process({
    "action": "rebalance"
})
# Returns: {"M111": 12500, "M112": 12500, ..., "M222": 12500}
```

---

## Scenario 10: Full Pipeline

**Description**: Complete end-to-end workflow using all four external interface types.

**Path**: `M111 → M122 → M211 → M222`

**External Interfaces**: YAML, Database, LLM API, PDF

**Token Consumption**: ~350 tokens

**Steps**:
1. M111 reads YAML config (File I/O)
2. Config propagates: M111 → M110 → M100 → M000
3. M000 routes to M122 for database query (Database)
4. Query result: M122 → M120 → M100 → M000
5. M000 routes to M211 for LLM processing (API)
6. LLM result: M211 → M210 → M200 → M000
7. M000 routes to M222 for PDF generation (File I/O)
8. PDF created: M222 → M220 → M200 → M000
9. Complete workflow finished

**Code Example**:
```python
result = root.process({
    "action": "full_pipeline",
    "config_path": "config/settings.yaml",
    "tenant_id": 123,
    "generate_report": True
})
```

---

## Summary Table

| # | Scenario | Path | Tokens | Interface |
|---|----------|------|--------|-----------|
| 1 | Config Load | M111→M110→M100→M000 | ~120 | YAML File |
| 2 | Tenant Query | M122→M120→M100→M000 | ~180 | Database |
| 3 | Excel Import | M121→M120→M100→M000 | ~150 | Excel File |
| 4 | MCP Tool Call | M000→M200→M210→M211 | ~200 | LLM API |
| 5 | PDF Generation | M000→M200→M220→M222 | ~160 | PDF File |
| 6 | Web API Request | M221→M220→M200→M000 | ~140 | HTTP REST |
| 7 | Hierarchical Merge | M110+M120→M100 | ~130 | Multiple |
| 8 | Error Propagation | M122→M120→M100 | ~90 | Database |
| 9 | Load Rebalancing | M000→all leaves | ~80 | Internal |
| 10 | Full Pipeline | M111→M122→M211→M222 | ~350 | All types |

**Total Token Consumption**: ~1,350 tokens

---

## Running Simulations

```bash
# Run all 10 scenarios
python scripts/run_scenarios.py

# Run specific scenario
python scripts/run_scenarios.py --scenario 10

# Run with verbose output
python scripts/run_scenarios.py --verbose
```

---

## References

- See [technical_report.md](technical_report.md) for detailed analysis
- See [RESEARCH.md](RESEARCH.md) for experiment results
- See [CONFIG.md](CONFIG.md) for token budget configuration
