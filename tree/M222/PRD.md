# M222 - PDF Generator PRD

## Overview
The PDF Generator (M222) is a leaf node responsible for all PDF file generation including tenant reports and system documentation.

## Node Information
- **Node ID**: M222
- **Level**: 3 (Leaf)
- **Type**: Interface
- **Parent**: M220 (Output Handler)
- **Children**: None (Leaf node)

## Responsibilities
1. Generate PDF reports from data
2. Apply templates and styling
3. Support multiple report types
4. Handle PDF file output

## External Interfaces
**File I/O** - PDF files (.pdf)

This is a LEAF node - it is the only level that interfaces with external systems.

## Dependencies
- FileInterface (shared/interfaces)
- MockPDFInterface for testing

## API Actions
| Action | Description |
|--------|-------------|
| `generate` | Generate PDF from data |
| `template` | Apply PDF template |
| `export` | Export PDF to file |

## Input/Output Format
```json
{
  "action": "generate",
  "template": "tenant_report",
  "data": {
    "tenant_id": 123,
    "name": "John Doe",
    "unit": "A101"
  },
  "output_path": "reports/tenant_123.pdf"
}
```

## Token Budget
- Default allocation: 6,000 tokens
- Generate operation: 50 + pages * 20
- Template: 30 tokens
- Export: 10 tokens

## Success Criteria
- [x] Generate PDF reports correctly
- [x] Apply templates properly
- [x] Track token consumption
- [x] Unit tests passing
