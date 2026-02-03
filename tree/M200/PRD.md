# M200 - Application Manager PRD

## Overview
The Application Manager (M200) coordinates server and output operations. It acts as the central hub for all application-facing services in the right subtree.

## Node Information
- **Node ID**: M200
- **Level**: 1 (Manager)
- **Type**: Manager
- **Parent**: M000 (Root Orchestrator)
- **Children**: M210 (Left - Server Handler), M220 (Right - Output Handler)

## Responsibilities
1. Coordinate server and output operations between children
2. Aggregate application status from subtree
3. Handle MCP tool calls and output generation workflows
4. Route requests to appropriate child node
5. Manage token budget for application subtree

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M210 (Server Handler)
- M220 (Output Handler)

## API Actions
| Action | Description |
|--------|-------------|
| `serve` | Handle server-related requests |
| `output` | Handle output generation requests |
| `status` | Get application subtree status |
| `route` | Route request to appropriate child |

## Token Budget
- Default allocation: 60% of parent budget (M000)
- Distribution: Split between M210 and M220 based on usage weights

## Success Criteria
- [x] Successfully coordinates M210 and M220
- [x] Server and output operations work correctly
- [x] Token tracking accurate for subtree
- [x] Unit tests passing
