"""
Tests for M210 - Server Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M210.src.main import ServerHandlerNode, create_node


class TestServerHandlerNode:
    """Tests for the Server Handler node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M210"
        assert node.config.name == "Server Handler"
        assert node.left is not None  # M211
        assert node.right is not None  # M212

    def test_children_initialized(self):
        """Test that children M211 and M212 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M211"
        assert node.right.node_id == "M212"

    def test_process_call_tool(self):
        """Test calling an MCP tool."""
        node = create_node()
        result = node.process({
            "action": "call_tool",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        })
        assert result.success
        assert "tool" in result.data

    def test_process_get_resource(self):
        """Test getting an MCP resource."""
        node = create_node()
        result = node.process({
            "action": "get_resource",
            "resource": "prompt://tenant-report"
        })
        assert result.success

    def test_process_execute_with_prompt(self):
        """Test executing tool with prompt context."""
        node = create_node()
        result = node.process({
            "action": "execute_with_prompt",
            "resource": "prompt://tenant-report",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1},
            "variables": {"name": "Test"}
        })
        assert result.success
        assert "tool_result" in result.data

    def test_process_list_capabilities(self):
        """Test listing capabilities."""
        node = create_node()
        result = node.process({"action": "list_capabilities"})
        assert result.success
        assert "tools" in result.data
        assert "resources" in result.data

    def test_process_status(self):
        """Test getting server status."""
        node = create_node()
        result = node.process({"action": "status"})
        assert result.success
        assert "server_healthy" in result.data

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown_action"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_call_tool(self):
        """Test convenience call_tool method."""
        node = create_node()
        result = node.call_tool("get_tenant_info", {"tenant_id": 1})
        assert result is not None

    def test_convenience_get_prompt(self):
        """Test convenience get_prompt method."""
        node = create_node()
        prompt = node.get_prompt("prompt://tenant-report")
        assert isinstance(prompt, str)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "list_capabilities"})
        assert result.tokens_used > 0
        assert result.node_id == "M210"
