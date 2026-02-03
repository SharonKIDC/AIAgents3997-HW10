# M120 - Database Handler PRD

## Overview
The Database Handler (M120) coordinates all data persistence operations including Excel file processing and SQL database queries.

## Node Information
- **Node ID**: M120
- **Level**: 2 (Handler)
- **Type**: Handler
- **Parent**: M100 (Infrastructure Manager)
- **Children**: M121 (Left - Excel Handler), M122 (Right - SQL Database)

## Responsibilities
1. Coordinate Excel and SQL database operations
2. Aggregate database status from leaf children
3. Handle combined data operations (Excel import → SQL insert)
4. Route requests to appropriate leaf node
5. Manage token budget for database subtree

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M121 (Excel Handler)
- M122 (SQL Database)

## API Actions
| Action | Description |
|--------|-------------|
| `read_excel` | Read Excel file via M121 |
| `query_db` | Execute SQL query via M122 |
| `import_data` | Import Excel data to database |
| `status` | Get database subtree status |

## Token Budget
- Default allocation: 50% of parent budget (M100)
- Distribution: 40% to M121, 60% to M122

## Success Criteria
- [x] Successfully coordinates M121 and M122
- [x] Excel and database operations work correctly
- [x] Token tracking accurate for subtree
- [x] Unit tests passing
