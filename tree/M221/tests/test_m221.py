"""
Tests for M221 - Web Interface Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M221.src.main import WebInterfaceNode, MockHTTPInterface, create_node


class TestMockHTTPInterface:
    """Tests for the mock HTTP interface."""

    def test_get_tenants(self):
        """Test GET request for tenants."""
        interface = MockHTTPInterface()
        result = interface.get("/api/tenants")
        assert result.success
        assert len(result.data) > 0

    def test_get_tenant_by_id(self):
        """Test GET request for specific tenant."""
        interface = MockHTTPInterface()
        result = interface.get("/api/tenants/1")
        assert result.success
        assert result.data["id"] == 1

    def test_get_nonexistent_tenant(self):
        """Test GET request for non-existent tenant."""
        interface = MockHTTPInterface()
        result = interface.get("/api/tenants/999")
        assert not result.success

    def test_post_tenant(self):
        """Test POST request to create tenant."""
        interface = MockHTTPInterface()
        result = interface.post("/api/tenants", {"name": "New Tenant", "unit": "301"})
        assert result.success
        assert "id" in result.data

    def test_put_tenant(self):
        """Test PUT request to update tenant."""
        interface = MockHTTPInterface()
        result = interface.put("/api/tenants/1", {"name": "Updated Name"})
        assert result.success

    def test_delete_tenant(self):
        """Test DELETE request to remove tenant."""
        interface = MockHTTPInterface()
        result = interface.delete("/api/tenants/1")
        assert result.success


class TestWebInterfaceNode:
    """Tests for the Web Interface node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M221"
        assert node.config.name == "Web Interface Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_get(self):
        """Test GET request."""
        node = create_node()
        result = node.process({
            "method": "GET",
            "url": "/api/tenants"
        })
        assert result.success
        assert isinstance(result.data, list)

    def test_process_post(self):
        """Test POST request."""
        node = create_node()
        result = node.process({
            "method": "POST",
            "url": "/api/tenants",
            "data": {"name": "Test Tenant", "unit": "401"}
        })
        assert result.success

    def test_process_put(self):
        """Test PUT request."""
        node = create_node()
        result = node.process({
            "method": "PUT",
            "url": "/api/tenants/1",
            "data": {"name": "Updated"}
        })
        assert result.success

    def test_process_delete(self):
        """Test DELETE request."""
        node = create_node()
        result = node.process({
            "method": "DELETE",
            "url": "/api/tenants/2"
        })
        assert result.success

    def test_process_unknown_method(self):
        """Test handling unknown HTTP method."""
        node = create_node()
        result = node.process({"method": "PATCH", "url": "/api/test"})
        assert not result.success
        assert "Unknown method" in result.error

    def test_convenience_api_get(self):
        """Test convenience api_get method."""
        node = create_node()
        result = node.api_get("/api/tenants")
        assert result is not None
        assert len(result) > 0

    def test_convenience_api_post(self):
        """Test convenience api_post method."""
        node = create_node()
        result = node.api_post("/api/tenants", {"name": "Test"})
        assert result is not None

    def test_convenience_get_tenants(self):
        """Test convenience get_tenants method."""
        node = create_node()
        tenants = node.get_tenants()
        assert isinstance(tenants, list)

    def test_convenience_create_tenant(self):
        """Test convenience create_tenant method."""
        node = create_node()
        result = node.create_tenant({"name": "New", "unit": "501"})
        assert result is not None

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "method": "GET",
            "url": "/api/tenants"
        })
        assert result.tokens_used > 0
        assert result.node_id == "M221"
