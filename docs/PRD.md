# Product Requirements Document (PRD)

## BST Orchestration Architecture for AI Agent Management

### Project Overview

**Project Name**: BST Orchestration (HW10)
**Version**: 1.0.0
**Author**: Student
**Date**: 2024-01-15
**Based On**: Dr. Rami Segal's "Managing an Army of Agents" - Section 9

---

## 1. Problem Statement

Managing multiple AI agents in a complex system requires structured coordination, resource allocation, and clear separation of concerns. Without proper orchestration, systems suffer from:
- Uncontrolled resource (token) consumption
- Unclear module boundaries
- Difficult testing and maintenance
- Poor scalability

## 2. Solution Overview

Implement a **Binary Spanning Tree (BST) Architecture** that:
- Decomposes systems into hierarchical binary tree structure
- Enforces the **Leaf Law**: external interfaces only in leaf nodes
- Provides token-based load balancing
- Enables bottom-up development and testing

## 3. Goals & Objectives

### Primary Goals
1. Create a 15-node BST with 4 levels
2. Demonstrate the Leaf Law principle
3. Implement token distribution algorithm
4. Validate with 10 scenario simulations

### Success Metrics
- All 15 nodes implemented and tested
- 80%+ test coverage per node
- All 10 scenarios execute successfully
- Clear documentation per node

## 4. Functional Requirements

### FR-1: Tree Structure
- **FR-1.1**: System must have exactly 15 nodes
- **FR-1.2**: Tree must have 4 levels (Root, Level 1, Level 2, Leaves)
- **FR-1.3**: Each internal node must have exactly 2 children

### FR-2: Leaf Law Compliance
- **FR-2.1**: Only leaf nodes (Level 3) may have external interfaces
- **FR-2.2**: Internal nodes must only communicate with children
- **FR-2.3**: External interfaces include: File I/O, Database, HTTP, APIs

### FR-3: Token Management
- **FR-3.1**: Root node manages total token budget
- **FR-3.2**: Tokens distributed to leaves via weighted algorithm
- **FR-3.3**: Each node tracks token consumption

### FR-4: Node Structure
- **FR-4.1**: Each node must have: PRD, PLAN, TODO, src/, tests/, config/
- **FR-4.2**: Each node must be independently testable
- **FR-4.3**: Each node must have a factory function

## 5. Non-Functional Requirements

### NFR-1: Performance
- Token query operations: O(1)
- Single leaf balance: O(log n)
- Full rebalance: O(n²) maximum

### NFR-2: Maintainability
- Modular node structure
- Clear interface contracts
- Comprehensive documentation

### NFR-3: Testability
- Unit tests per node
- Integration tests for parent-child
- Scenario-based system tests

## 6. Node Specifications

| Node | Name | Level | External Interface |
|------|------|-------|-------------------|
| M000 | Root Orchestrator | 0 | None |
| M100 | Infrastructure Manager | 1 | None |
| M200 | Application Manager | 1 | None |
| M110 | Config Handler | 2 | None |
| M120 | Database Handler | 2 | None |
| M210 | Server Handler | 2 | None |
| M220 | Output Handler | 2 | None |
| M111 | YAML Config | 3 | File I/O (YAML) |
| M112 | Log Writer | 3 | File I/O (Log) |
| M121 | Excel Handler | 3 | File I/O (Excel) |
| M122 | SQL Database | 3 | SQLite/PostgreSQL |
| M211 | MCP Tools | 3 | External API (LLM) |
| M212 | MCP Resources | 3 | External API |
| M221 | Web Interface | 3 | HTTP (REST) |
| M222 | PDF Generator | 3 | File I/O (PDF) |

## 7. Acceptance Criteria

- [ ] 15 nodes in binary tree structure
- [ ] Leaf Law enforced (no external I/O in internal nodes)
- [ ] Token distribution algorithm implemented
- [ ] O notation analysis documented
- [ ] 10 scenarios execute successfully
- [ ] 80%+ test coverage
- [ ] All documentation complete

## 8. Out of Scope

- Real external service integration (mocks used)
- Production deployment
- Performance optimization beyond O notation requirements
- Multi-machine distribution

## 9. Dependencies

- Python 3.9+
- pytest, coverage.py
- No external runtime dependencies (all interfaces mocked)

## 10. Timeline

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Leaf nodes (M111-M222) | Complete |
| Phase 2 | Level 2 nodes (M110-M220) | Complete |
| Phase 3 | Level 1 nodes (M100, M200) | Complete |
| Phase 4 | Root node (M000) | Complete |
| Phase 5 | Testing & Documentation | Complete |
