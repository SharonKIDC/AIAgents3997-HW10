# BST Orchestration - HW10

Binary Spanning Tree Architecture for AI Agent Orchestration

Based on Dr. Rami Segal's "Managing an Army of Agents" textbook, Section 9.

## Tree Map

```
                              [ROOT - M000]
                         Tenant Manager Core
                        /                    \
                 [M100]                        [M200]
            Infrastructure                  Application
              /        \                     /        \
          [M110]      [M120]            [M210]      [M220]
         Config      Database           Server      Output
         /    \       /    \            /    \       /    \
    [M111][M112][M121][M122]       [M211][M212][M221][M222]
    YAML  Logs  Excel  SQL         Tools Rsrc  Web   PDF
    I/O   File  File   DB          API   API   HTTP  File
```

## Node Summary

| Level | Node | Name | Type | External Interface |
|-------|------|------|------|-------------------|
| 0 | M000 | Root Orchestrator | Orchestrator | None |
| 1 | M100 | Infrastructure Manager | Manager | None |
| 1 | M200 | Application Manager | Manager | None |
| 2 | M110 | Config Handler | Handler | None |
| 2 | M120 | Database Handler | Handler | None |
| 2 | M210 | Server Handler | Handler | None |
| 2 | M220 | Output Handler | Handler | None |
| 3 | M111 | YAML Config | Interface | File I/O (YAML) |
| 3 | M112 | Log Writer | Interface | File I/O (Log) |
| 3 | M121 | Excel Handler | Interface | File I/O (Excel) |
| 3 | M122 | SQL Database | Interface | SQLite/PostgreSQL |
| 3 | M211 | MCP Tools | Interface | External API (LLM) |
| 3 | M212 | MCP Resources | Interface | External API |
| 3 | M221 | Web Interface | Interface | HTTP (REST API) |
| 3 | M222 | PDF Generator | Interface | File I/O (PDF) |

**Total Nodes**: 15 | **Levels**: 4 | **Leaf Nodes**: 8

## Architecture Principles

### Leaf Law
External interfaces (databases, APIs, files) are ONLY in leaf nodes (Level 3).
Internal nodes (Levels 0-2) coordinate their children without direct external I/O.

### Bottom-Up Development
1. **Leaves first** (M111-M222): Implement and test each leaf independently
2. **Level 2** (M110-M220): Integrate child pairs
3. **Level 1** (M100, M200): Integrate subtrees
4. **Root** (M000): Final system integration

### Token Budget Distribution
The root node distributes a token budget across all leaves using a weighted algorithm:
- O(1) for token queries
- O(log n) for single leaf balance
- O(n²) for full rebalance

## Quick Start

```bash
# Run all tests
pip install pytest pytest-cov
python -m pytest -v

# Run coverage
python scripts/run_coverage.py --html

# Run linter
python scripts/run_linter.py

# Run 10 scenario simulations
python scripts/run_scenarios.py
```

## Coverage Table

| Node | Module | Coverage |
|------|--------|----------|
| Shared | token_balancer.py | 85%+ |
| M000 | main.py | 80%+ |
| M111 | main.py | 90%+ |
| M122 | main.py | 85%+ |
| ... | ... | ... |

*Run `python scripts/run_coverage.py --table` for full report*

## Scenario Simulations

| # | Scenario | Path |
|---|----------|------|
| 1 | Config Load | M111 → M110 → M100 → M000 |
| 2 | Tenant Query | M122 → M120 → M100 → M000 |
| 3 | Excel Import | M121 → M120 → M100 → M000 |
| 4 | MCP Tool Call | M000 → M200 → M210 → M211 |
| 5 | PDF Generation | M000 → M200 → M220 → M222 |
| 6 | Web API Request | M221 → M220 → M200 → M000 |
| 7 | Hierarchical Merge | M110 + M120 → M100 |
| 8 | Error Propagation | M122 → M120 → M100 (retry) |
| 9 | Load Rebalancing | All leaves via M000 |
| 10 | Full Pipeline | M111 → M122 → M211 → M222 |

## Repository Structure

```
AIAgents3997-HW10/
├── README.md                 # This file
├── pyproject.toml            # Project configuration
├── docs/
│   ├── technical_report.md   # Full technical report
│   ├── optimization_comparison.md
│   └── scenario_simulations.md
├── tree/
│   ├── M000/                 # Root node
│   ├── M100/, M200/          # Level 1
│   ├── M110/, M120/, M210/, M220/  # Level 2
│   └── M111/-M222/           # Leaves (Level 3)
├── shared/
│   ├── types/                # Node type definitions
│   ├── utils/                # TokenBalancer, etc.
│   └── interfaces/           # External interface contracts
└── scripts/
    ├── run_coverage.py
    ├── run_linter.py
    └── run_scenarios.py
```

## Node Structure

Each node directory contains:
```
node_Mxxx/
├── PRD.md              # Product requirements
├── PLAN.md             # Implementation plan
├── TODO.md             # Task tracking
├── src/
│   ├── __init__.py
│   └── main.py         # Node implementation
├── tests/
│   └── test_main.py    # Unit tests
├── config/
│   └── config.json     # Node configuration
└── README.md           # Node documentation
```

## Source Project

This BST decomposition is based on:
- **HW8**: Residential Complex Tenant Management System
- **Location**: `/root/Git/AIAgents3997-HW8`
- **Original Stats**: 174 tests, 81.81% coverage

## References

1. Segal, R. (2024). *Managing an Army of Agents: Binary Spanning Tree Architecture for Huge Systems*.
2. Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
3. Adelson-Velsky, G. M., & Landis, E. M. (1962). An algorithm for the organization of information.
4. Souravlas, S., et al. (2019). A novel probabilistic model for scheduling in shared processor systems.

## License

MIT License - Educational Use
