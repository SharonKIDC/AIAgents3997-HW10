"""
Tests for M220 - Output Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M220.src.main import OutputHandlerNode, create_node


class TestOutputHandlerNode:
    """Tests for the Output Handler node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M220"
        assert node.config.name == "Output Handler"
        assert node.left is not None  # M221
        assert node.right is not None  # M222

    def test_children_initialized(self):
        """Test that children M221 and M222 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M221"
        assert node.right.node_id == "M222"

    def test_process_api_request_get(self):
        """Test API GET request."""
        node = create_node()
        result = node.process({
            "action": "api_request",
            "method": "GET",
            "url": "/api/tenants"
        })
        assert result.success

    def test_process_api_request_post(self):
        """Test API POST request."""
        node = create_node()
        result = node.process({
            "action": "api_request",
            "method": "POST",
            "url": "/api/tenants",
            "data": {"name": "Test"}
        })
        assert result.success

    def test_process_generate_pdf(self):
        """Test PDF generation."""
        node = create_node()
        result = node.process({
            "action": "generate_pdf",
            "report_type": "tenant_statement",
            "data": {"tenant_id": 1, "name": "Test"}
        })
        assert result.success

    def test_process_fetch_and_report(self):
        """Test fetch and report combined action."""
        node = create_node()
        result = node.process({
            "action": "fetch_and_report",
            "url": "/api/tenants",
            "report_type": "balance_summary"
        })
        assert result.success
        assert "api_data" in result.data
        assert "pdf_info" in result.data

    def test_process_multi_output(self):
        """Test multi-output generation."""
        node = create_node()
        result = node.process({
            "action": "multi_output",
            "report_type": "tenant_statement",
            "data": {"tenant_id": 1}
        })
        assert result.success
        assert "outputs" in result.data

    def test_process_list_outputs(self):
        """Test listing available outputs."""
        node = create_node()
        result = node.process({"action": "list_outputs"})
        assert result.success
        assert "pdf_documents" in result.data
        assert "api_endpoints" in result.data

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown_action"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_api_get(self):
        """Test convenience api_get method."""
        node = create_node()
        result = node.api_get("/api/tenants")
        assert result is not None

    def test_convenience_generate_report(self):
        """Test convenience generate_report method."""
        node = create_node()
        result = node.generate_report("tenant_statement", {"tenant_id": 1})
        assert isinstance(result, dict)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "action": "api_request",
            "method": "GET",
            "url": "/api/test"
        })
        assert result.tokens_used > 0
        assert result.node_id == "M220"
