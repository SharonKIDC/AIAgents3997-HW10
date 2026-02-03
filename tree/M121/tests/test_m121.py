"""
Tests for M121 - Excel Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M121.src.main import ExcelHandlerNode, MockExcelInterface, create_node


class TestMockExcelInterface:
    """Tests for the mock Excel interface."""

    def test_read_existing_file(self):
        """Test reading an existing Excel file."""
        interface = MockExcelInterface()
        result = interface.read("tenants.xlsx")
        assert result.success
        assert "Sheet1" in result.data

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        interface = MockExcelInterface()
        result = interface.read("nonexistent.xlsx")
        assert not result.success

    def test_write(self):
        """Test writing an Excel file."""
        interface = MockExcelInterface()
        result = interface.write("test.xlsx", {"Sheet1": [{"a": 1}]})
        assert result.success

    def test_exists(self):
        """Test checking if file exists."""
        interface = MockExcelInterface()
        assert interface.exists("tenants.xlsx")
        assert not interface.exists("nonexistent.xlsx")

    def test_get_sheet(self):
        """Test getting a specific sheet."""
        interface = MockExcelInterface()
        data = interface.get_sheet("tenants.xlsx", "Sheet1")
        assert len(data) > 0

    def test_add_row(self):
        """Test adding a row to a sheet."""
        interface = MockExcelInterface()
        result = interface.add_row("tenants.xlsx", "Sheet1", {"id": 99})
        assert result


class TestExcelHandlerNode:
    """Tests for the Excel Handler node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M121"
        assert node.config.name == "Excel Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_read(self):
        """Test reading Excel file."""
        node = create_node()
        result = node.process({
            "action": "read",
            "path": "tenants.xlsx"
        })
        assert result.success

    def test_process_write(self):
        """Test writing Excel file."""
        node = create_node()
        result = node.process({
            "action": "write",
            "path": "test.xlsx",
            "data": {"Sheet1": [{"id": 1}]}
        })
        assert result.success

    def test_process_get_sheet(self):
        """Test getting a sheet."""
        node = create_node()
        result = node.process({
            "action": "get_sheet",
            "path": "tenants.xlsx",
            "sheet": "Sheet1"
        })
        assert result.success
        assert isinstance(result.data, list)

    def test_process_add_row(self):
        """Test adding a row."""
        node = create_node()
        result = node.process({
            "action": "add_row",
            "path": "tenants.xlsx",
            "sheet": "Sheet1",
            "data": {"id": 100, "name": "Test"}
        })
        assert result.success

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_get_tenants(self):
        """Test convenience get_tenants method."""
        node = create_node()
        tenants = node.get_tenants()
        assert isinstance(tenants, list)
        assert len(tenants) > 0

    def test_convenience_add_tenant(self):
        """Test convenience add_tenant method."""
        node = create_node()
        success = node.add_tenant({"id": 101, "name": "New Tenant"})
        assert success

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "read", "path": "tenants.xlsx"})
        assert result.tokens_used > 0
        assert result.node_id == "M121"
