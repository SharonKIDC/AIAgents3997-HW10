# M000 - Root Orchestrator PRD

## Overview
The Root Orchestrator (M000) is the central coordination point for the entire BST architecture. It manages system-wide operations, token distribution, and workflow execution.

## Node Information
- **Node ID**: M000
- **Level**: 0 (Root)
- **Type**: Orchestrator
- **Parent**: None
- **Children**: M100 (Left), M200 (Right)

## Responsibilities
1. System initialization and shutdown coordination
2. Token budget distribution across all leaf nodes
3. Workflow orchestration spanning multiple subtrees
4. System status monitoring and reporting
5. Load balancing and rebalancing operations

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M100 (Infrastructure Manager)
- M200 (Application Manager)
- TokenBalancer utility

## API Actions
| Action | Description |
|--------|-------------|
| `initialize` | Initialize entire system |
| `full_workflow` | Execute multi-step workflow |
| `route_request` | Route to appropriate subtree |
| `rebalance` | Redistribute token budget |
| `status` | Get system-wide status |

## Token Budget
- Default allocation: 100,000 tokens
- Distribution: Split between M100 and M200 subtrees based on weights

## Success Criteria
- [ ] Successfully coordinates all 15 nodes
- [ ] Token distribution works correctly
- [ ] All 10 scenarios execute successfully
- [ ] System status accurately reflects tree state
