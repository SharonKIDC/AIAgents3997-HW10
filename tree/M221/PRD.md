# M221 - Web Interface PRD

## Overview
The Web Interface (M221) is a leaf node responsible for all HTTP/REST operations including web API responses and client communication.

## Node Information
- **Node ID**: M221
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M220 (Output Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Handle HTTP requests (GET, POST, PUT, DELETE)
2. Send HTTP responses to clients
3. Manage session state
4. Handle API authentication

## External Interfaces
**HTTP** - REST API

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- HTTPInterface (shared/interfaces)
- MockHTTPInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `request` | Make HTTP request |
| `respond` | Send HTTP response |
| `validate` | Validate request parameters |

## Input/Output Format
```json
{
  "action": "respond",
  "status": 200,
  "data": {
    "tenant_id": 123,
    "name": "John Doe"
  }
}
```

## Token Budget
- Default allocation: 8,000 tokens
- Request operation: 15 + body_size/100
- Response operation: 10 + body_size/100

## Success Criteria
- [x] Handle HTTP requests correctly
- [x] Send responses with proper status codes
- [x] Track token consumption
- [x] Unit tests passing
