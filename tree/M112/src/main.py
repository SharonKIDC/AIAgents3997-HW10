"""
M112 - Log Writer Handler
Leaf Node: External Interface - File I/O (log files)

Maps to HW8: logging_config/
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import FileInterface, InterfaceResult


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class MockLogInterface(FileInterface):
    """Mock log file interface for testing."""

    def __init__(self):
        self._logs: Dict[str, List[str]] = {}
        self._default_path = "logs/app.log"

    def read(self, path: str) -> InterfaceResult:
        """Read log file contents."""
        logs = self._logs.get(path, [])
        content = "\n".join(logs)
        return InterfaceResult(
            success=True,
            data={"lines": logs, "count": len(logs)},
            bytes_transferred=len(content)
        )

    def write(self, path: str, data: Any) -> InterfaceResult:
        """Append log entry to file."""
        if path not in self._logs:
            self._logs[path] = []

        if isinstance(data, str):
            self._logs[path].append(data)
        elif isinstance(data, list):
            self._logs[path].extend(data)

        return InterfaceResult(
            success=True,
            data={"path": path, "entries": len(self._logs[path])},
            bytes_transferred=len(str(data))
        )

    def exists(self, path: str) -> bool:
        """Check if log file exists."""
        return path in self._logs

    def clear(self, path: str) -> None:
        """Clear log file."""
        if path in self._logs:
            self._logs[path] = []


class LogWriterNode(LeafNode):
    """
    M112 - Log Writer Leaf Node

    Responsibility: Handle all logging file I/O
    External Interface: File system (log files)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M112",
            name="Log Writer Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M110",
            token_budget=3000,
            metadata={"interface": "log_file", "file_types": [".log", ".txt"]}
        )
        super().__init__(config)
        self._interface_type = "log_file"
        self._interface: Optional[MockLogInterface] = None
        self._connected = False
        self._log_format = "%(timestamp)s - %(level)s - %(node)s - %(message)s"

    def connect(self) -> bool:
        """Connect to file system interface."""
        self._interface = MockLogInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from file system."""
        self._interface = None
        self._connected = False

    def _format_log_entry(self, level: LogLevel, message: str, node_id: str = "M112") -> str:
        """Format a log entry."""
        timestamp = datetime.now().isoformat()
        return f"{timestamp} - {level.name} - {node_id} - {message}"

    def process(self, input_data: Any) -> NodeResult:
        """
        Process logging request.

        Input format:
        {
            "action": "log" | "read" | "clear",
            "level": "INFO" | "DEBUG" | "WARNING" | "ERROR" | "CRITICAL",
            "message": "Log message",
            "path": "logs/app.log",
            "node_id": "M111"  # Source node
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 5  # Base token cost

        action = input_data.get("action", "log")
        path = input_data.get("path", "logs/app.log")

        try:
            if action == "log":
                level_str = input_data.get("level", "INFO")
                level = LogLevel[level_str]
                message = input_data.get("message", "")
                node_id = input_data.get("node_id", self.node_id)

                entry = self._format_log_entry(level, message, node_id)
                result = self._interface.write(path, entry)
                tokens_used += len(message) // 100

            elif action == "read":
                result = self._interface.read(path)
                tokens_used += result.bytes_transferred // 200

            elif action == "clear":
                self._interface.clear(path)
                result = InterfaceResult(success=True, data={"cleared": path})

            else:
                return NodeResult(
                    success=False,
                    error=f"Unknown action: {action}",
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            self.consume_tokens(tokens_used)

            return NodeResult(
                success=result.success,
                data=result.data,
                error=result.error,
                tokens_used=tokens_used,
                node_id=self.node_id
            )

        except Exception as e:
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def log(self, level: str, message: str, node_id: str = None) -> bool:
        """Convenience method to write a log entry."""
        result = self.process({
            "action": "log",
            "level": level,
            "message": message,
            "node_id": node_id or self.node_id
        })
        return result.success

    def info(self, message: str, node_id: str = None) -> bool:
        return self.log("INFO", message, node_id)

    def error(self, message: str, node_id: str = None) -> bool:
        return self.log("ERROR", message, node_id)

    def debug(self, message: str, node_id: str = None) -> bool:
        return self.log("DEBUG", message, node_id)

    def warning(self, message: str, node_id: str = None) -> bool:
        return self.log("WARNING", message, node_id)


# Factory function
def create_node() -> LogWriterNode:
    """Create and return M112 node instance."""
    return LogWriterNode()
