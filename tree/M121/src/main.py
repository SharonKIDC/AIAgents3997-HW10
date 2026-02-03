"""
M121 - Excel Handler
Leaf Node: External Interface - File I/O (Excel .xlsx files)

Maps to HW8: excel_manager.py, excel_operations.py
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import FileInterface, InterfaceResult


@dataclass
class TenantRecord:
    """Tenant data record."""
    id: int
    name: str
    unit: str
    phone: str
    email: str
    rent: float
    balance: float = 0.0


class MockExcelInterface(FileInterface):
    """Mock Excel file interface for testing."""

    def __init__(self):
        self._workbooks: Dict[str, Dict[str, List[Dict]]] = {}
        self._init_sample_data()

    def _init_sample_data(self):
        """Initialize sample tenant data."""
        self._workbooks["tenants.xlsx"] = {
            "Sheet1": [
                {"id": 1, "name": "John Doe", "unit": "101", "phone": "555-0101", "email": "john@example.com", "rent": 1500.0, "balance": 0.0},
                {"id": 2, "name": "Jane Smith", "unit": "102", "phone": "555-0102", "email": "jane@example.com", "rent": 1600.0, "balance": 100.0},
                {"id": 3, "name": "Bob Wilson", "unit": "201", "phone": "555-0201", "email": "bob@example.com", "rent": 1400.0, "balance": -50.0},
            ]
        }

    def read(self, path: str) -> InterfaceResult:
        """Read Excel file."""
        if path not in self._workbooks:
            return InterfaceResult(
                success=False,
                error=f"File not found: {path}"
            )

        data = self._workbooks[path]
        return InterfaceResult(
            success=True,
            data=data,
            bytes_transferred=len(str(data))
        )

    def write(self, path: str, data: Any) -> InterfaceResult:
        """Write to Excel file."""
        self._workbooks[path] = data
        return InterfaceResult(
            success=True,
            data={"path": path, "sheets": list(data.keys())},
            bytes_transferred=len(str(data))
        )

    def exists(self, path: str) -> bool:
        """Check if Excel file exists."""
        return path in self._workbooks

    def get_sheet(self, path: str, sheet: str) -> List[Dict]:
        """Get specific sheet from workbook."""
        if path in self._workbooks and sheet in self._workbooks[path]:
            return self._workbooks[path][sheet]
        return []

    def add_row(self, path: str, sheet: str, row: Dict) -> bool:
        """Add row to sheet."""
        if path not in self._workbooks:
            self._workbooks[path] = {}
        if sheet not in self._workbooks[path]:
            self._workbooks[path][sheet] = []
        self._workbooks[path][sheet].append(row)
        return True


class ExcelHandlerNode(LeafNode):
    """
    M121 - Excel Handler Leaf Node

    Responsibility: Handle all Excel file I/O operations
    External Interface: File system (Excel .xlsx files)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M121",
            name="Excel Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M120",
            token_budget=8000,
            metadata={"interface": "excel_file", "file_types": [".xlsx", ".xls"]}
        )
        super().__init__(config)
        self._interface_type = "excel_file"
        self._interface: Optional[MockExcelInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to file system interface."""
        self._interface = MockExcelInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from file system."""
        self._interface = None
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process Excel file request.

        Input format:
        {
            "action": "read" | "write" | "get_sheet" | "add_row",
            "path": "tenants.xlsx",
            "sheet": "Sheet1",
            "data": {...}  # For write/add_row
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 15  # Base token cost for Excel operations

        action = input_data.get("action", "read")
        path = input_data.get("path", "tenants.xlsx")
        sheet = input_data.get("sheet", "Sheet1")

        try:
            if action == "read":
                result = self._interface.read(path)
                tokens_used += result.bytes_transferred // 50

            elif action == "write":
                data = input_data.get("data", {})
                result = self._interface.write(path, data)
                tokens_used += result.bytes_transferred // 25

            elif action == "get_sheet":
                sheet_data = self._interface.get_sheet(path, sheet)
                result = InterfaceResult(
                    success=True,
                    data=sheet_data,
                    bytes_transferred=len(str(sheet_data))
                )
                tokens_used += len(sheet_data) * 5

            elif action == "add_row":
                row_data = input_data.get("data", {})
                success = self._interface.add_row(path, sheet, row_data)
                result = InterfaceResult(
                    success=success,
                    data={"added": row_data}
                )
                tokens_used += 20

            else:
                return NodeResult(
                    success=False,
                    error=f"Unknown action: {action}",
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            self.consume_tokens(tokens_used)

            return NodeResult(
                success=result.success,
                data=result.data,
                error=result.error,
                tokens_used=tokens_used,
                node_id=self.node_id
            )

        except Exception as e:
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def get_tenants(self, path: str = "tenants.xlsx") -> List[Dict]:
        """Convenience method to get all tenants."""
        result = self.process({"action": "get_sheet", "path": path, "sheet": "Sheet1"})
        return result.data if result.success else []

    def add_tenant(self, tenant: Dict, path: str = "tenants.xlsx") -> bool:
        """Convenience method to add a tenant."""
        result = self.process({
            "action": "add_row",
            "path": path,
            "sheet": "Sheet1",
            "data": tenant
        })
        return result.success


# Factory function
def create_node() -> ExcelHandlerNode:
    """Create and return M121 node instance."""
    return ExcelHandlerNode()
