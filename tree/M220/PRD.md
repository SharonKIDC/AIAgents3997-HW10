# M220 - Output Handler PRD

## Overview
The Output Handler (M220) coordinates all output generation operations including web interface responses and PDF report generation.

## Node Information
- **Node ID**: M220
- **Level**: 2 (Handler)
- **Type**: Handler
- **Parent**: M200 (Application Manager)
- **Children**: M221 (Left - Web Interface), M222 (Right - PDF Generator)

## Responsibilities
1. Coordinate web and PDF output operations
2. Aggregate output status from leaf children
3. Handle combined output operations (web response + PDF generation)
4. Route requests to appropriate leaf node
5. Manage token budget for output subtree

## External Interfaces
**None** - Internal node (external interfaces only in leaves)

## Dependencies
- M221 (Web Interface)
- M222 (PDF Generator)

## API Actions
| Action | Description |
|--------|-------------|
| `send_response` | Send HTTP response via M221 |
| `generate_pdf` | Generate PDF report via M222 |
| `aggregate` | Combine web and PDF outputs |
| `status` | Get output subtree status |

## Token Budget
- Default allocation: 40% of parent budget (M200)
- Distribution: 50% to M221, 50% to M222

## Success Criteria
- [x] Successfully coordinates M221 and M222
- [x] Web and PDF output operations work correctly
- [x] Token tracking accurate for subtree
- [x] Unit tests passing
