"""
Tests for M212 - MCP Resources Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M212.src.main import MCPResourcesNode, MockMCPResourcesInterface, ResourceType, create_node


class TestMockMCPResourcesInterface:
    """Tests for the mock MCP Resources interface."""

    def test_call_existing_resource(self):
        """Test fetching an existing resource."""
        interface = MockMCPResourcesInterface()
        result = interface.call("prompt://tenant-report", {"uri": "prompt://tenant-report"})
        assert result.success
        assert "content" in result.data

    def test_call_nonexistent_resource(self):
        """Test fetching a non-existent resource."""
        interface = MockMCPResourcesInterface()
        result = interface.call("nonexistent://uri", {"uri": "nonexistent://uri"})
        assert not result.success

    def test_render_with_variables(self):
        """Test rendering a template with variables."""
        interface = MockMCPResourcesInterface()
        result = interface.call("prompt://tenant-report", {
            "uri": "prompt://tenant-report",
            "variables": {"tenant_name": "John", "unit": "101"}
        })
        assert result.success
        assert "rendered" in result.data["content"]

    def test_get_status(self):
        """Test getting interface status."""
        interface = MockMCPResourcesInterface()
        status = interface.get_status()
        assert status["available"]
        assert status["resources_count"] > 0

    def test_list_resources(self):
        """Test listing available resources."""
        interface = MockMCPResourcesInterface()
        resources = interface.list_resources()
        assert len(resources) > 0


class TestMCPResourcesNode:
    """Tests for the MCP Resources node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M212"
        assert node.config.name == "MCP Resources Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_fetch(self):
        """Test fetching a resource."""
        node = create_node()
        result = node.process({
            "action": "fetch",
            "uri": "prompt://tenant-report"
        })
        assert result.success
        assert "content" in result.data

    def test_process_render(self):
        """Test rendering a prompt with variables."""
        node = create_node()
        result = node.process({
            "action": "render",
            "uri": "prompt://tenant-report",
            "variables": {"tenant_name": "Jane", "unit": "202"}
        })
        assert result.success

    def test_process_list(self):
        """Test listing resources."""
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

    def test_convenience_get_prompt(self):
        """Test convenience get_prompt method."""
        node = create_node()
        prompt = node.get_prompt("prompt://tenant-report", {"tenant_name": "Test", "unit": "101"})
        assert isinstance(prompt, str)

    def test_convenience_get_schema(self):
        """Test convenience get_schema method."""
        node = create_node()
        schema = node.get_schema("schema://tenant")
        assert isinstance(schema, dict)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "action": "fetch",
            "uri": "prompt://tenant-report"
        })
        assert result.tokens_used > 0
        assert result.node_id == "M212"
