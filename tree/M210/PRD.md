# M210 - Server Handler PRD

## Overview
The Server Handler (M210) coordinates all MCP server-related operations including tool calls and resource management.

## Node Information
- **Node ID**: M210
- **Level**: 2 (Handler)
- **Type**: Handler
- **Parent**: M200 (Application Manager)
- **Children**: M211 (Left - MCP Tools), M212 (Right - MCP Resources)

## Responsibilities
1. Coordinate MCP tool calls and resource operations
2. Aggregate server status from leaf children
3. Handle combined MCP operations (call tool + access resources)
4. Route requests to appropriate leaf node
5. Manage token budget for server subtree

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M211 (MCP Tools)
- M212 (MCP Resources)

## API Actions
| Action | Description |
|--------|-------------|
| `call_tool` | Execute MCP tool via M211 |
| `get_resource` | Access resource via M212 |
| `aggregate` | Combine tool and resource responses |
| `status` | Get server subtree status |

## Token Budget
- Default allocation: 60% of parent budget (M200)
- Distribution: 70% to M211, 30% to M212

## Success Criteria
- [x] Successfully coordinates M211 and M212
- [x] MCP tool and resource operations work correctly
- [x] Token tracking accurate for subtree
- [x] Unit tests passing
