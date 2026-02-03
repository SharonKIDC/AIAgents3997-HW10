"""
Tests for M110 - Config Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M110.src.main import ConfigHandlerNode, create_node


class TestConfigHandlerNode:
    """Tests for the Config Handler node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M110"
        assert node.config.name == "Config Handler"
        assert node.left is not None  # M111
        assert node.right is not None  # M112

    def test_children_initialized(self):
        """Test that children M111 and M112 are properly initialized."""
        node = create_node()
        assert node.left.node_id == "M111"
        assert node.right.node_id == "M112"

    def test_process_load_config(self):
        """Test loading configuration."""
        node = create_node()
        result = node.process({
            "action": "load_config",
            "config_path": "config/settings.yaml"
        })
        assert result.success
        assert result.data is not None

    def test_process_save_config(self):
        """Test saving configuration."""
        node = create_node()
        result = node.process({
            "action": "save_config",
            "config_path": "config/test.yaml",
            "data": {"debug": True, "log_level": "INFO"}
        })
        assert result.success

    def test_process_log(self):
        """Test logging through M112."""
        node = create_node()
        result = node.process({
            "action": "log",
            "log_level": "INFO",
            "message": "Test log message"
        })
        assert result.success

    def test_process_init_system(self):
        """Test system initialization."""
        node = create_node()
        result = node.process({
            "action": "init_system",
            "config_path": "config/settings.yaml"
        })
        assert result.success
        assert "config" in result.data
        assert "initialized" in result.data

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown_action"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_get_config(self):
        """Test convenience get_config method."""
        node = create_node()
        config = node.get_config()
        assert isinstance(config, dict)

    def test_convenience_log(self):
        """Test convenience log method."""
        node = create_node()
        success = node.log("INFO", "Test message")
        assert success

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({"action": "load_config"})
        assert result.tokens_used > 0
        assert result.node_id == "M110"
