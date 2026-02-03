# 10 Scenario Simulations

This document details the 10 scenario simulations required by Section 9 of the homework.

## Scenario 1: Config Load

**Description**: Load YAML configuration and propagate to all modules.

**Path**: `M111 → M110 → M100 → M000`

**External Interface**: File I/O (YAML)

**Steps**:
1. M000 receives initialization request
2. Routes to M100 (Infrastructure Manager)
3. M100 delegates to M110 (Config Handler)
4. M110 calls M111 (YAML Config leaf)
5. M111 reads YAML file from disk
6. Configuration data returns up the tree

**Token Consumption**: ~50-100 tokens

---

## Scenario 2: Tenant Query

**Description**: Query tenant data from SQL database.

**Path**: `M122 → M120 → M100 → M000`

**External Interface**: SQLite/PostgreSQL Database

**Steps**:
1. Request for tenant data arrives at M000
2. Routes to M100 → M120 (Database Handler)
3. M120 delegates to M122 (SQL Database leaf)
4. M122 executes SQL query
5. Results return up to M000

**Token Consumption**: ~60-120 tokens

---

## Scenario 3: Excel Import

**Description**: Import tenant data from Excel spreadsheet.

**Path**: `M121 → M120 → M100 → M000`

**External Interface**: File I/O (Excel .xlsx)

**Steps**:
1. Import request arrives at M000
2. Routes to M100 → M120 (Database Handler)
3. M120 delegates to M121 (Excel Handler leaf)
4. M121 reads Excel file
5. Data parsed and returned up tree

**Token Consumption**: ~80-150 tokens

---

## Scenario 4: MCP Tool Call

**Description**: Invoke external LLM tool via MCP protocol.

**Path**: `M000 → M200 → M210 → M211`

**External Interface**: External API (LLM)

**Steps**:
1. Tool call request at M000
2. Routes to M200 (Application Manager)
3. M200 delegates to M210 (Server Handler)
4. M210 calls M211 (MCP Tools leaf)
5. M211 invokes external LLM API
6. Response propagates back up

**Token Consumption**: ~100-200 tokens

---

## Scenario 5: PDF Generation

**Description**: Generate PDF report for tenant.

**Path**: `M000 → M200 → M220 → M222`

**External Interface**: File I/O (PDF)

**Steps**:
1. Report generation request at M000
2. Routes to M200 (Application Manager)
3. M200 delegates to M220 (Output Handler)
4. M220 calls M222 (PDF Generator leaf)
5. M222 generates PDF file
6. File path/status returned up tree

**Token Consumption**: ~80-150 tokens

---

## Scenario 6: Web API Request

**Description**: Handle incoming REST API request.

**Path**: `M221 → M220 → M200 → M000`

**External Interface**: HTTP (REST API)

**Steps**:
1. HTTP request received at M221 (Web Interface leaf)
2. Processed and forwarded to M220
3. M220 coordinates response
4. Bubbles up to M200, then M000
5. Response sent back through same path

**Token Consumption**: ~50-100 tokens

---

## Scenario 7: Hierarchical Merge

**Description**: Merge configuration and database data.

**Path**: `M110 + M120 → M100`

**External Interfaces**: None (internal aggregation)

**Steps**:
1. M100 requests data from both children
2. M110 returns configuration data
3. M120 returns database data
4. M100 merges results
5. Combined result returned to M000

**Token Consumption**: ~100-180 tokens

---

## Scenario 8: Error Propagation

**Description**: Database error bubbles up with retry logic.

**Path**: `M122 → M120 → M100 (retry)`

**External Interface**: Database (error case)

**Steps**:
1. M122 attempts database operation
2. Operation fails (connection error, timeout, etc.)
3. Error propagates to M120
4. M120 may attempt retry via M122
5. If retry fails, error propagates to M100
6. M100 logs error and returns failure status

**Token Consumption**: ~40-100 tokens

---

## Scenario 9: Load Rebalancing

**Description**: Redistribute token budget across all leaves.

**Path**: All leaves via M000

**External Interfaces**: None (internal operation)

**Steps**:
1. Rebalance triggered at M000 (manual or automatic)
2. TokenBalancer recalculates weights for all leaves
3. New allocations distributed to M111-M222
4. Each leaf updates its token budget
5. Utilization report generated

**Token Consumption**: ~200-500 tokens

**Complexity**: O(n²) for full rebalance

---

## Scenario 10: Full Pipeline

**Description**: Complete workflow from config through output.

**Path**: `M111 → M122 → M211 → M222`

**External Interfaces**: YAML, Database, LLM API, PDF

**Steps**:
1. M000 initiates full_pipeline workflow
2. **Config Phase**: M111 reads YAML config
3. **Query Phase**: M122 queries database for tenant
4. **Process Phase**: M211 processes data with LLM tool
5. **Output Phase**: M222 generates PDF report
6. All results aggregated at M000

**Token Consumption**: ~300-500 tokens

**Detailed Flow**:
```
M000 (start)
  ├─→ M100 ─→ M110 ─→ M111 (YAML read)     [External I/O]
  │   └─← config data ←─┘
  │
  ├─→ M100 ─→ M120 ─→ M122 (SQL query)     [External I/O]
  │   └─← tenant data ←─┘
  │
  ├─→ M200 ─→ M210 ─→ M211 (MCP tool)      [External API]
  │   └─← processed result ←─┘
  │
  └─→ M200 ─→ M220 ─→ M222 (PDF gen)       [External I/O]
      └─← report info ←─┘
```

---

## Summary Table

| # | Scenario | External I/O | Est. Tokens |
|---|----------|-------------|-------------|
| 1 | Config Load | YAML file | 50-100 |
| 2 | Tenant Query | SQL DB | 60-120 |
| 3 | Excel Import | Excel file | 80-150 |
| 4 | MCP Tool Call | LLM API | 100-200 |
| 5 | PDF Generation | PDF file | 80-150 |
| 6 | Web API Request | HTTP | 50-100 |
| 7 | Hierarchical Merge | None | 100-180 |
| 8 | Error Propagation | DB (error) | 40-100 |
| 9 | Load Rebalancing | None | 200-500 |
| 10 | Full Pipeline | All | 300-500 |

---

## Running Simulations

```bash
# Run all 10 scenarios
python scripts/run_scenarios.py

# Output includes:
# - Success/failure status for each scenario
# - Token consumption
# - Nodes traversed
# - Execution details
```
