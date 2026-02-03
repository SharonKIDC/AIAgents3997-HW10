"""
Tests for M211 - MCP Tools Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M211.src.main import MCPToolsNode, MockMCPToolsInterface, ToolType, create_node


class TestMockMCPToolsInterface:
    """Tests for the mock MCP Tools interface."""

    def test_call_existing_tool(self):
        """Test calling an existing tool."""
        interface = MockMCPToolsInterface()
        result = interface.call("/tools/get_tenant_info", {"tenant_id": 1})
        assert result.success
        assert "output" in result.data

    def test_call_nonexistent_tool(self):
        """Test calling a non-existent tool."""
        interface = MockMCPToolsInterface()
        result = interface.call("/tools/nonexistent", {})
        assert not result.success

    def test_get_status(self):
        """Test getting interface status."""
        interface = MockMCPToolsInterface()
        status = interface.get_status()
        assert status["available"]
        assert status["tools_count"] > 0

    def test_list_tools(self):
        """Test listing available tools."""
        interface = MockMCPToolsInterface()
        tools = interface.list_tools()
        assert len(tools) > 0
        assert any(t.name == "get_tenant_info" for t in tools)


class TestMCPToolsNode:
    """Tests for the MCP Tools node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M211"
        assert node.config.name == "MCP Tools Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_call_tool(self):
        """Test calling a tool."""
        node = create_node()
        result = node.process({
            "action": "call",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        })
        assert result.success
        assert "output" in result.data

    def test_process_call_calculate_balance(self):
        """Test calling calculate_balance tool."""
        node = create_node()
        result = node.process({
            "action": "call",
            "tool": "calculate_balance",
            "params": {"tenant_id": 1, "include_fees": True}
        })
        assert result.success

    def test_process_list(self):
        """Test listing tools."""
        node = create_node()
        result = node.process({"action": "list"})
        assert result.success
        assert isinstance(result.data, list)
        assert len(result.data) > 0

    def test_process_status(self):
        """Test getting status."""
        node = create_node()
        result = node.process({"action": "status"})
        assert result.success
        assert "available" in result.data

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_call_tool(self):
        """Test convenience call_tool method."""
        node = create_node()
        result = node.call_tool("get_tenant_info", {"tenant_id": 1})
        assert result is not None

    def test_convenience_list_available_tools(self):
        """Test convenience list_available_tools method."""
        node = create_node()
        tools = node.list_available_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "action": "call",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        })
        assert result.tokens_used > 0
        assert result.node_id == "M211"
