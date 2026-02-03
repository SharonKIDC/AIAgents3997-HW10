"""
Unit tests for M111 - YAML Config Handler (Leaf Node)

Tests cover:
- Configuration reading
- Configuration writing
- Mock interface operations
- Token consumption tracking
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M111.src.main import YAMLConfigNode, MockYAMLInterface, create_node


class TestMockYAMLInterface:
    """Test suite for MockYAMLInterface."""

    def test_read_default_config(self):
        """Test reading returns default configuration."""
        interface = MockYAMLInterface()
        result = interface.read("config/settings.yaml")

        assert result.success
        assert "database" in result.data
        assert "logging" in result.data
        assert "api" in result.data

    def test_write_and_read(self):
        """Test writing and reading back configuration."""
        interface = MockYAMLInterface()

        # Write custom config
        custom_config = {"custom": "value", "number": 42}
        write_result = interface.write("custom.yaml", custom_config)
        assert write_result.success

        # Read it back
        read_result = interface.read("custom.yaml")
        assert read_result.success
        assert read_result.data == custom_config

    def test_exists(self):
        """Test file existence check."""
        interface = MockYAMLInterface()

        assert not interface.exists("nonexistent.yaml")

        interface.write("test.yaml", {"key": "value"})
        assert interface.exists("test.yaml")


class TestYAMLConfigNode:
    """Test suite for YAMLConfigNode (M111)."""

    def test_node_creation(self):
        """Test node factory and initialization."""
        node = create_node()

        assert node.node_id == "M111"
        assert node.is_leaf
        assert node._interface_type == "yaml_file"

    def test_connect_disconnect(self):
        """Test connection lifecycle."""
        node = create_node()

        assert not node._connected
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_read_action(self):
        """Test processing read action."""
        node = create_node()

        result = node.process({
            "action": "read",
            "path": "config/settings.yaml"
        })

        assert result.success
        assert result.node_id == "M111"
        assert result.tokens_used > 0
        assert "database" in result.data

    def test_process_write_action(self):
        """Test processing write action."""
        node = create_node()

        result = node.process({
            "action": "write",
            "path": "test_config.yaml",
            "data": {"test": "data"}
        })

        assert result.success
        assert result.tokens_used > 0

    def test_process_unknown_action(self):
        """Test handling of unknown action."""
        node = create_node()

        result = node.process({
            "action": "invalid_action"
        })

        assert not result.success
        assert "Unknown action" in result.error

    def test_load_config_convenience(self):
        """Test convenience method for loading config."""
        node = create_node()

        config = node.load_config()

        assert isinstance(config, dict)
        assert "database" in config

    def test_save_config_convenience(self):
        """Test convenience method for saving config."""
        node = create_node()

        success = node.save_config({"key": "value"}, "output.yaml")

        assert success

    def test_token_consumption(self):
        """Test that token consumption is tracked."""
        node = create_node()
        initial_remaining = node.tokens_remaining

        node.process({"action": "read", "path": "config/settings.yaml"})

        assert node.tokens_remaining < initial_remaining

    def test_get_status(self):
        """Test status reporting."""
        node = create_node()
        node.connect()

        status = node.get_status()

        assert status["node_id"] == "M111"
        assert status["interface_type"] == "yaml_file"
        assert "tokens_remaining" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
