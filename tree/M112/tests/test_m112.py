"""
Tests for M112 - Log Writer Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M112.src.main import LogWriterNode, MockLogInterface, LogLevel, create_node


class TestMockLogInterface:
    """Tests for the mock log interface."""

    def test_write_and_read(self):
        """Test writing and reading log entries."""
        interface = MockLogInterface()
        write_result = interface.write("logs/test.log", "Test entry")
        assert write_result.success

        read_result = interface.read("logs/test.log")
        assert read_result.success
        assert "Test entry" in read_result.data["lines"]

    def test_clear(self):
        """Test clearing log file."""
        interface = MockLogInterface()
        interface.write("logs/test.log", "Entry 1")
        interface.clear("logs/test.log")
        result = interface.read("logs/test.log")
        assert result.data["count"] == 0

    def test_exists(self):
        """Test checking if log file exists."""
        interface = MockLogInterface()
        assert not interface.exists("logs/new.log")
        interface.write("logs/new.log", "Entry")
        assert interface.exists("logs/new.log")


class TestLogWriterNode:
    """Tests for the Log Writer node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M112"
        assert node.config.name == "Log Writer Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_log_info(self):
        """Test logging INFO level."""
        node = create_node()
        result = node.process({
            "action": "log",
            "level": "INFO",
            "message": "Info message"
        })
        assert result.success

    def test_process_log_error(self):
        """Test logging ERROR level."""
        node = create_node()
        result = node.process({
            "action": "log",
            "level": "ERROR",
            "message": "Error message"
        })
        assert result.success

    def test_process_log_debug(self):
        """Test logging DEBUG level."""
        node = create_node()
        result = node.process({
            "action": "log",
            "level": "DEBUG",
            "message": "Debug message"
        })
        assert result.success

    def test_process_read(self):
        """Test reading log file."""
        node = create_node()
        # Write first
        node.process({"action": "log", "level": "INFO", "message": "Test"})
        # Then read
        result = node.process({"action": "read"})
        assert result.success
        assert "lines" in result.data

    def test_process_clear(self):
        """Test clearing log file."""
        node = create_node()
        result = node.process({"action": "clear"})
        assert result.success

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_log(self):
        """Test convenience log method."""
        node = create_node()
        assert node.log("INFO", "Test message")

    def test_convenience_info(self):
        """Test convenience info method."""
        node = create_node()
        assert node.info("Info message")

    def test_convenience_error(self):
        """Test convenience error method."""
        node = create_node()
        assert node.error("Error message")

    def test_convenience_debug(self):
        """Test convenience debug method."""
        node = create_node()
        assert node.debug("Debug message")

    def test_convenience_warning(self):
        """Test convenience warning method."""
        node = create_node()
        assert node.warning("Warning message")

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "action": "log",
            "level": "INFO",
            "message": "Test"
        })
        assert result.tokens_used > 0
        assert result.node_id == "M112"
