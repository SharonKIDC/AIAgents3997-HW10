# M121 - Excel Handler PRD

## Overview
The Excel Handler (M121) is a leaf node responsible for all Excel file I/O operations including reading tenant data and exporting reports.

## Node Information
- **Node ID**: M121
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M120 (Database Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Read Excel files (.xlsx, .xls)
2. Write/export data to Excel files
3. Parse tenant data from spreadsheets
4. Validate Excel file structure

## External Interfaces
**File I/O** - Excel files (.xlsx, .xls)

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- FileInterface (shared/interfaces)
- MockExcelInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `read` | Read data from Excel file |
| `write` | Write data to Excel file |
| `validate` | Validate Excel file structure |

## Input/Output Format
```json
{
  "action": "read",
  "path": "data/tenants.xlsx",
  "sheet": "Tenants"
}
```

## Token Budget
- Default allocation: 5,000 tokens
- Read operation: 20 + rows * 3
- Write operation: 20 + rows * 5

## Success Criteria
- [x] Read Excel files correctly
- [x] Write Excel files correctly
- [x] Track token consumption
- [x] Unit tests passing
