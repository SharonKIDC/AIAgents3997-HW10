"""
Unit tests for M122 - SQL Database Handler (Leaf Node)

Tests cover:
- Database queries
- CRUD operations
- Mock database interface
- Token consumption tracking
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M122.src.main import SQLDatabaseNode, MockDatabaseInterface, create_node


class TestMockDatabaseInterface:
    """Test suite for MockDatabaseInterface."""

    def test_connect_disconnect(self):
        """Test connection lifecycle."""
        interface = MockDatabaseInterface()

        result = interface.connect("sqlite:///test.db")
        assert result.success
        assert interface._connected

        interface.disconnect()
        assert not interface._connected

    def test_query_tenants(self):
        """Test querying tenants table."""
        interface = MockDatabaseInterface()
        interface.connect("sqlite:///test.db")

        result = interface.query("SELECT * FROM tenants")

        assert result.success
        assert len(result.data) == 3  # Sample data has 3 tenants

    def test_query_with_params(self):
        """Test parameterized query."""
        interface = MockDatabaseInterface()
        interface.connect("sqlite:///test.db")

        result = interface.query(
            "SELECT * FROM tenants WHERE id = :id",
            {"id": 1}
        )

        assert result.success
        assert len(result.data) == 1
        assert result.data[0]["name"] == "John Doe"

    def test_insert_tenant(self):
        """Test inserting a new tenant."""
        interface = MockDatabaseInterface()
        interface.connect("sqlite:///test.db")

        result = interface.execute(
            "INSERT INTO tenants",
            {"name": "New Tenant", "unit": "301", "rent": 1200.0}
        )

        assert result.success
        assert result.data["action"] == "insert"
        assert result.data["id"] == 4  # Next auto-increment

    def test_query_not_connected(self):
        """Test query when not connected."""
        interface = MockDatabaseInterface()

        result = interface.query("SELECT * FROM tenants")

        assert not result.success
        assert "Not connected" in result.error


class TestSQLDatabaseNode:
    """Test suite for SQLDatabaseNode (M122)."""

    def test_node_creation(self):
        """Test node factory and initialization."""
        node = create_node()

        assert node.node_id == "M122"
        assert node.is_leaf
        assert node._interface_type == "database"

    def test_auto_connect_on_process(self):
        """Test automatic connection on process."""
        node = create_node()

        assert not node._connected
        node.process({"action": "get_tenants"})
        assert node._connected

    def test_process_get_tenants(self):
        """Test processing get_tenants action."""
        node = create_node()

        result = node.process({"action": "get_tenants"})

        assert result.success
        assert result.node_id == "M122"
        assert len(result.data) == 3

    def test_process_get_tenant_by_id(self):
        """Test getting a specific tenant."""
        node = create_node()

        result = node.process({
            "action": "get_tenant",
            "id": 1
        })

        assert result.success
        assert len(result.data) == 1

    def test_process_add_tenant(self):
        """Test adding a new tenant."""
        node = create_node()

        result = node.process({
            "action": "add_tenant",
            "data": {
                "name": "Test Tenant",
                "unit": "401",
                "rent": 1100.0
            }
        })

        assert result.success
        assert "id" in result.data

    def test_process_raw_query(self):
        """Test raw SQL query."""
        node = create_node()

        result = node.process({
            "action": "query",
            "sql": "SELECT * FROM tenants",
            "params": {}
        })

        assert result.success
        assert len(result.data) >= 3

    def test_process_get_payments(self):
        """Test getting tenant payments."""
        node = create_node()

        result = node.process({
            "action": "get_payments",
            "tenant_id": 1
        })

        assert result.success

    def test_process_unknown_action(self):
        """Test handling of unknown action."""
        node = create_node()

        result = node.process({"action": "invalid"})

        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_get_all_tenants(self):
        """Test convenience method."""
        node = create_node()

        tenants = node.get_all_tenants()

        assert isinstance(tenants, list)
        assert len(tenants) == 3

    def test_convenience_get_tenant(self):
        """Test get single tenant convenience method."""
        node = create_node()

        tenant = node.get_tenant(1)

        assert tenant is not None
        assert tenant["name"] == "John Doe"

    def test_token_tracking(self):
        """Test token consumption tracking."""
        node = create_node()
        initial = node.tokens_remaining

        node.process({"action": "get_tenants"})

        assert node.tokens_remaining < initial


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
