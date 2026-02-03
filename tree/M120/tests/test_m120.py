"""
Tests for M120 - Database Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M120.src.main import DatabaseHandlerNode, create_node


class TestDatabaseHandlerNode:
    """Tests for the Database Handler node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M120"
        assert node.config.name == "Database Handler"
        assert node.left is not None  # M121
        assert node.right is not None  # M122

    def test_children_initialized(self):
        """Test that children M121 and M122 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M121"
        assert node.right.node_id == "M122"

    def test_process_get_tenants_database(self):
        """Test getting tenants from database."""
        node = create_node()
        result = node.process({
            "action": "get_tenants",
            "source": "database"
        })
        assert result.success
        assert isinstance(result.data, list)

    def test_process_get_tenants_excel(self):
        """Test getting tenants from Excel."""
        node = create_node()
        result = node.process({
            "action": "get_tenants",
            "source": "excel"
        })
        assert result.success

    def test_process_get_tenants_both(self):
        """Test getting tenants from both sources."""
        node = create_node()
        result = node.process({
            "action": "get_tenants",
            "source": "both"
        })
        assert result.success
        assert "excel" in result.data
        assert "database" in result.data

    def test_process_add_tenant(self):
        """Test adding a tenant."""
        node = create_node()
        result = node.process({
            "action": "add_tenant",
            "data": {"name": "Test Tenant", "unit": "A101"},
            "sync_excel": True
        })
        assert result.success

    def test_process_import_excel(self):
        """Test importing from Excel."""
        node = create_node()
        result = node.process({
            "action": "import_excel",
            "path": "tenants.xlsx"
        })
        assert result.success
        assert "imported" in result.data

    def test_process_export_excel(self):
        """Test exporting to Excel."""
        node = create_node()
        result = node.process({
            "action": "export_excel",
            "path": "export.xlsx"
        })
        assert result.success
        assert "exported" in result.data

    def test_process_sync(self):
        """Test syncing Excel and database."""
        node = create_node()
        result = node.process({"action": "sync"})
        assert result.success
        assert "excel_count" in result.data
        assert "database_count" in result.data
        assert "in_sync" in result.data

    def test_process_query(self):
        """Test raw database query."""
        node = create_node()
        result = node.process({
            "action": "query",
            "sql": "SELECT * FROM tenants"
        })
        assert result.success

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown_action"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_get_all_tenants(self):
        """Test convenience get_all_tenants method."""
        node = create_node()
        tenants = node.get_all_tenants()
        assert isinstance(tenants, list)

    def test_convenience_add_tenant(self):
        """Test convenience add_tenant method."""
        node = create_node()
        success = node.add_tenant({"name": "New", "unit": "B202"})
        assert success

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "get_tenants"})
        assert result.tokens_used > 0
        assert result.node_id == "M120"
