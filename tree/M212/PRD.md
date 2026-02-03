# M212 - MCP Resources PRD

## Overview
The MCP Resources (M212) is a leaf node responsible for all MCP resource access including prompts, schemas, and static resources.

## Node Information
- **Node ID**: M212
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M210 (Server Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Access MCP resource endpoints
2. Manage resource caching
3. Handle resource versioning
4. Provide prompt templates

## External Interfaces
**External API** - MCP Resources

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- APIInterface (shared/interfaces)
- MockMCPResourcesInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `get` | Get resource by URI |
| `list` | List available resources |
| `template` | Get prompt template |

## Input/Output Format
```json
{
  "action": "get",
  "uri": "tenant://schemas/tenant_model"
}
```

## Token Budget
- Default allocation: 5,000 tokens
- Get operation: 20 + resource_size/100
- List operation: 30 tokens
- Template: 50 tokens

## Success Criteria
- [x] Access MCP resources correctly
- [x] Handle resource caching
- [x] Track token consumption
- [x] Unit tests passing
