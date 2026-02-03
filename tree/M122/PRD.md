# M122 - SQL Database PRD

## Overview
The SQL Database (M122) is a leaf node responsible for all database operations including queries, inserts, updates, and tenant data management.

## Node Information
- **Node ID**: M122
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M120 (Database Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
2. Manage database connections
3. Handle tenant CRUD operations
4. Validate query parameters to prevent SQL injection

## External Interfaces
**Database** - SQLite/PostgreSQL

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- DatabaseInterface (shared/interfaces)
- MockDatabaseInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `query` | Execute SELECT query |
| `insert` | Insert new record |
| `update` | Update existing record |
| `delete` | Delete record |

## Input/Output Format
```json
{
  "action": "query",
  "sql": "SELECT * FROM tenants WHERE id = ?",
  "params": [123]
}
```

## Token Budget
- Default allocation: 8,000 tokens
- Query operation: 15 + rows_returned * 5
- Insert/Update: 10 per operation
- Delete: 5 per operation

## Success Criteria
- [x] Execute SQL queries correctly
- [x] Parameterized queries (prevent SQL injection)
- [x] Track token consumption
- [x] Unit tests passing
