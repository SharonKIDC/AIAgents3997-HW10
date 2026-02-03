"""
Tests for M100 - Infrastructure Manager
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M100.src.main import InfrastructureManagerNode, create_node


class TestInfrastructureManagerNode:
    """Tests for the Infrastructure Manager node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M100"
        assert node.config.name == "Infrastructure Manager"
        assert node.left is not None  # M110
        assert node.right is not None  # M120

    def test_children_initialized(self):
        """Test that children M110 and M120 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M110"
        assert node.right.node_id == "M120"

    def test_process_system_status(self):
        """Test getting system status."""
        node = create_node()
        result = node.process({"action": "system_status"})
        assert result.success
        assert "initialized" in result.data
        assert "config_handler" in result.data
        assert "database_handler" in result.data

    def test_process_initialize(self):
        """Test system initialization."""
        node = create_node()
        result = node.process({
            "action": "initialize",
            "config_path": "config/settings.yaml"
        })
        assert result.success
        assert "config" in result.data
        assert "database_connected" in result.data

    def test_process_get_tenant_data(self):
        """Test getting tenant data."""
        node = create_node()
        result = node.process({
            "action": "get_tenant_data",
            "source": "database"
        })
        assert result.success
        assert "tenants" in result.data

    def test_process_get_tenant_data_with_config(self):
        """Test getting tenant data with config included."""
        node = create_node()
        result = node.process({
            "action": "get_tenant_data",
            "include_config": True
        })
        assert result.success
        assert "tenants" in result.data
        assert "config" in result.data

    def test_process_save_tenant(self):
        """Test saving tenant data."""
        node = create_node()
        result = node.process({
            "action": "save_tenant",
            "data": {"name": "Test Tenant", "unit": "A101"}
        })
        assert result.success

    def test_process_config_update(self):
        """Test configuration update."""
        node = create_node()
        result = node.process({
            "action": "config_update",
            "data": {"debug": True}
        })
        assert result.success

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown_action"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_initialize(self):
        """Test convenience initialize method."""
        node = create_node()
        success = node.initialize()
        assert success

    def test_convenience_get_tenants(self):
        """Test convenience get_tenants method."""
        node = create_node()
        tenants = node.get_tenants()
        assert isinstance(tenants, list)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "system_status"})
        assert result.tokens_used > 0
        assert result.node_id == "M100"
