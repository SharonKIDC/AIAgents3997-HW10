# M211 - MCP Tools PRD

## Overview
The MCP Tools (M211) is a leaf node responsible for all MCP tool invocations including LLM interactions and external API calls.

## Node Information
- **Node ID**: M211
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M210 (Server Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Execute MCP tool calls to external LLMs
2. Handle tool request/response formatting
3. Manage API authentication and rate limiting
4. Track LLM token consumption

## External Interfaces
**External API** - LLM/MCP Tools

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- APIInterface (shared/interfaces)
- MockMCPToolsInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `call` | Execute MCP tool call |
| `list` | List available tools |
| `validate` | Validate tool parameters |

## Input/Output Format
```json
{
  "action": "call",
  "tool_name": "tenant_search",
  "params": {
    "query": "find all tenants in building A"
  }
}
```

## Token Budget
- Default allocation: 20,000 tokens
- Tool call: varies by LLM response
- List operation: 50 tokens
- Validation: 10 tokens

## Success Criteria
- [x] Execute MCP tool calls correctly
- [x] Handle API errors gracefully
- [x] Track token consumption accurately
- [x] Unit tests passing
