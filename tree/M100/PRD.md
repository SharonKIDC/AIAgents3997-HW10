# M100 - Infrastructure Manager PRD

## Overview
The Infrastructure Manager (M100) coordinates configuration and data persistence operations. It acts as the central hub for all infrastructure-related services in the left subtree.

## Node Information
- **Node ID**: M100
- **Level**: 1 (Manager)
- **Type**: Manager
- **Parent**: M000 (Root Orchestrator)
- **Children**: M110 (Left - Config Handler), M120 (Right - Database Handler)

## Responsibilities
1. Coordinate configuration management operations between children
2. Aggregate infrastructure status from subtree
3. Handle config + database merge operations
4. Route requests to appropriate child node
5. Manage token budget for infrastructure subtree

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M110 (Config Handler)
- M120 (Database Handler)

## API Actions
| Action | Description |
|--------|-------------|
| `configure` | Initialize infrastructure configuration |
| `aggregate` | Merge data from config and database |
| `status` | Get infrastructure subtree status |
| `route` | Route request to appropriate child |

## Token Budget
- Default allocation: 40% of parent budget (M000)
- Distribution: Split between M110 and M120 based on usage weights

## Success Criteria
- [x] Successfully coordinates M110 and M120
- [x] Config and database operations work correctly
- [x] Token tracking accurate for subtree
- [x] Unit tests passing
