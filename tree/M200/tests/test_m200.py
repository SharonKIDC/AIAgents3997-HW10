"""
Tests for M200 - Application Manager
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M200.src.main import ApplicationManagerNode, create_node


class TestApplicationManagerNode:
    """Tests for the Application Manager node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M200"
        assert node.config.name == "Application Manager"
        assert node.left is not None  # M210
        assert node.right is not None  # M220

    def test_children_initialized(self):
        """Test that children M210 and M220 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M210"
        assert node.right.node_id == "M220"

    def test_process_status(self):
        """Test getting application status."""
        node = create_node()
        result = node.process({"action": "status"})
        assert result.success
        assert "application_running" in result.data
        assert "server_handler" in result.data

    def test_process_request_api(self):
        """Test processing API request."""
        node = create_node()
        result = node.process({
            "action": "process_request",
            "request_type": "api",
            "method": "GET",
            "url": "/api/tenants"
        })
        assert result.success

    def test_process_request_tool(self):
        """Test processing tool request."""
        node = create_node()
        result = node.process({
            "action": "process_request",
            "request_type": "tool",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        })
        assert result.success

    def test_process_request_report(self):
        """Test processing report request."""
        node = create_node()
        result = node.process({
            "action": "process_request",
            "request_type": "report",
            "report_type": "tenant_statement",
            "data": {"tenant_id": 1}
        })
        assert result.success

    def test_process_generate_report(self):
        """Test generating a report."""
        node = create_node()
        result = node.process({
            "action": "generate_report",
            "report_type": "tenant_statement",
            "data": {"tenant_id": 1, "name": "Test"}
        })
        assert result.success
        assert "report" in result.data

    def test_process_execute_tool(self):
        """Test executing an MCP tool."""
        node = create_node()
        result = node.process({
            "action": "execute_tool",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        })
        assert result.success

    def test_process_full_pipeline(self):
        """Test full application pipeline."""
        node = create_node()
        result = node.process({
            "action": "full_pipeline",
            "tenant_id": 1,
            "report_type": "tenant_statement"
        })
        assert result.success
        assert "tenant_data" in result.data
        assert "pipeline_steps" in result.data

    def test_process_capabilities(self):
        """Test getting application capabilities."""
        node = create_node()
        result = node.process({"action": "capabilities"})
        assert result.success
        assert "server" in result.data
        assert "outputs" in result.data

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

    def test_convenience_generate_tenant_report(self):
        """Test convenience generate_tenant_report method."""
        node = create_node()
        result = node.generate_tenant_report({"tenant_id": 1})
        assert isinstance(result, dict)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "status"})
        assert result.tokens_used > 0
        assert result.node_id == "M200"
