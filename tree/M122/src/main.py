"""
M122 - SQL Database Handler
Leaf Node: External Interface - SQLite/PostgreSQL Database

Maps to HW8: models.py, queries.py
"""
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import DatabaseInterface, InterfaceResult


@dataclass
class Tenant:
    """Tenant model."""
    id: Optional[int] = None
    name: str = ""
    unit: str = ""
    phone: str = ""
    email: str = ""
    rent: float = 0.0
    balance: float = 0.0


@dataclass
class Payment:
    """Payment model."""
    id: Optional[int] = None
    tenant_id: int = 0
    amount: float = 0.0
    date: str = ""
    method: str = ""


class MockDatabaseInterface(DatabaseInterface):
    """Mock database interface for testing."""

    def __init__(self):
        self._connected = False
        self._tables: Dict[str, List[Dict]] = {}
        self._auto_increment: Dict[str, int] = {}
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema with sample data."""
        self._tables["tenants"] = [
            {"id": 1, "name": "John Doe", "unit": "101", "phone": "555-0101", "email": "john@example.com", "rent": 1500.0, "balance": 0.0},
            {"id": 2, "name": "Jane Smith", "unit": "102", "phone": "555-0102", "email": "jane@example.com", "rent": 1600.0, "balance": 100.0},
            {"id": 3, "name": "Bob Wilson", "unit": "201", "phone": "555-0201", "email": "bob@example.com", "rent": 1400.0, "balance": -50.0},
        ]
        self._tables["payments"] = [
            {"id": 1, "tenant_id": 1, "amount": 1500.0, "date": "2024-01-01", "method": "check"},
            {"id": 2, "tenant_id": 2, "amount": 1600.0, "date": "2024-01-01", "method": "transfer"},
        ]
        self._auto_increment["tenants"] = 4
        self._auto_increment["payments"] = 3

    def connect(self, connection_string: str) -> InterfaceResult:
        """Connect to database."""
        self._connected = True
        return InterfaceResult(
            success=True,
            data={"connected": True, "database": connection_string}
        )

    def disconnect(self) -> None:
        """Disconnect from database."""
        self._connected = False

    def query(self, sql: str, params: Optional[Dict] = None) -> InterfaceResult:
        """Execute SELECT query."""
        if not self._connected:
            return InterfaceResult(success=False, error="Not connected")

        sql_lower = sql.lower()
        params = params or {}

        # Simple SQL parsing for mock
        if "select" in sql_lower:
            if "from tenants" in sql_lower:
                data = self._tables.get("tenants", [])
                if "where" in sql_lower and "id" in params:
                    data = [t for t in data if t["id"] == params["id"]]
                elif "where" in sql_lower and "unit" in params:
                    data = [t for t in data if t["unit"] == params["unit"]]
            elif "from payments" in sql_lower:
                data = self._tables.get("payments", [])
                if "tenant_id" in params:
                    data = [p for p in data if p["tenant_id"] == params["tenant_id"]]
            else:
                data = []

            return InterfaceResult(
                success=True,
                data=data,
                bytes_transferred=len(str(data))
            )

        return InterfaceResult(success=False, error="Invalid query")

    def execute(self, sql: str, params: Optional[Dict] = None) -> InterfaceResult:
        """Execute INSERT/UPDATE/DELETE."""
        if not self._connected:
            return InterfaceResult(success=False, error="Not connected")

        sql_lower = sql.lower()
        params = params or {}

        if "insert" in sql_lower:
            if "tenants" in sql_lower:
                new_id = self._auto_increment.get("tenants", 1)
                record = {**params, "id": new_id}
                self._tables["tenants"].append(record)
                self._auto_increment["tenants"] = new_id + 1
                return InterfaceResult(success=True, data={"id": new_id, "action": "insert"})

            elif "payments" in sql_lower:
                new_id = self._auto_increment.get("payments", 1)
                record = {**params, "id": new_id}
                self._tables["payments"].append(record)
                self._auto_increment["payments"] = new_id + 1
                return InterfaceResult(success=True, data={"id": new_id, "action": "insert"})

        elif "update" in sql_lower:
            if "tenants" in sql_lower and "id" in params:
                for tenant in self._tables["tenants"]:
                    if tenant["id"] == params["id"]:
                        tenant.update({k: v for k, v in params.items() if k != "id"})
                        return InterfaceResult(success=True, data={"action": "update", "id": params["id"]})

        elif "delete" in sql_lower:
            if "tenants" in sql_lower and "id" in params:
                self._tables["tenants"] = [t for t in self._tables["tenants"] if t["id"] != params["id"]]
                return InterfaceResult(success=True, data={"action": "delete", "id": params["id"]})

        return InterfaceResult(success=False, error="Invalid statement")


class SQLDatabaseNode(LeafNode):
    """
    M122 - SQL Database Leaf Node

    Responsibility: Handle all database operations
    External Interface: SQLite/PostgreSQL Database
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M122",
            name="SQL Database Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M120",
            token_budget=10000,
            metadata={"interface": "database", "db_types": ["sqlite", "postgresql"]}
        )
        super().__init__(config)
        self._interface_type = "database"
        self._interface: Optional[MockDatabaseInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to database."""
        self._interface = MockDatabaseInterface()
        result = self._interface.connect("sqlite:///tenant.db")
        self._connected = result.success
        return self._connected

    def disconnect(self) -> None:
        """Disconnect from database."""
        if self._interface:
            self._interface.disconnect()
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process database request.

        Input format:
        {
            "action": "query" | "execute" | "get_tenant" | "add_tenant" | "get_payments",
            "sql": "SELECT * FROM tenants",
            "params": {"id": 1},
            "data": {...}  # For insert/update
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 20  # Base token cost for DB operations

        action = input_data.get("action", "query")

        try:
            if action == "query":
                sql = input_data.get("sql", "")
                params = input_data.get("params", {})
                result = self._interface.query(sql, params)
                tokens_used += result.bytes_transferred // 20

            elif action == "execute":
                sql = input_data.get("sql", "")
                params = input_data.get("params", {})
                result = self._interface.execute(sql, params)
                tokens_used += 30

            elif action == "get_tenant":
                tenant_id = input_data.get("id")
                result = self._interface.query(
                    "SELECT * FROM tenants WHERE id = :id",
                    {"id": tenant_id}
                )
                tokens_used += 25

            elif action == "get_tenants":
                result = self._interface.query("SELECT * FROM tenants")
                tokens_used += len(result.data) * 5 if result.success else 10

            elif action == "add_tenant":
                data = input_data.get("data", {})
                result = self._interface.execute(
                    "INSERT INTO tenants",
                    data
                )
                tokens_used += 40

            elif action == "get_payments":
                tenant_id = input_data.get("tenant_id")
                result = self._interface.query(
                    "SELECT * FROM payments WHERE tenant_id = :tenant_id",
                    {"tenant_id": tenant_id}
                )
                tokens_used += len(result.data) * 3 if result.success else 10

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

    def get_all_tenants(self) -> List[Dict]:
        """Convenience method to get all tenants."""
        result = self.process({"action": "get_tenants"})
        return result.data if result.success else []

    def get_tenant(self, tenant_id: int) -> Optional[Dict]:
        """Convenience method to get a tenant by ID."""
        result = self.process({"action": "get_tenant", "id": tenant_id})
        if result.success and result.data:
            return result.data[0] if isinstance(result.data, list) else result.data
        return None


# Factory function
def create_node() -> SQLDatabaseNode:
    """Create and return M122 node instance."""
    return SQLDatabaseNode()
