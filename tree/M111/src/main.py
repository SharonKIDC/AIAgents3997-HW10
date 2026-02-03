"""
M111 - YAML Configuration Handler
Leaf Node: External Interface - File I/O (YAML files)

Maps to HW8: config/settings.py
"""
from typing import Any, Dict, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import FileInterface, InterfaceResult


class MockYAMLInterface(FileInterface):
    """Mock YAML file interface for testing."""

    def __init__(self):
        self._storage: Dict[str, Dict] = {}
        self._default_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "tenant_db"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False
            }
        }

    def read(self, path: str) -> InterfaceResult:
        """Read YAML configuration file."""
        if path in self._storage:
            return InterfaceResult(
                success=True,
                data=self._storage[path],
                bytes_transferred=len(str(self._storage[path]))
            )
        # Return default config for demo
        return InterfaceResult(
            success=True,
            data=self._default_config.copy(),
            bytes_transferred=len(str(self._default_config))
        )

    def write(self, path: str, data: Any) -> InterfaceResult:
        """Write YAML configuration file."""
        self._storage[path] = data
        return InterfaceResult(
            success=True,
            data={"path": path, "written": True},
            bytes_transferred=len(str(data))
        )

    def exists(self, path: str) -> bool:
        """Check if config file exists."""
        return path in self._storage


class YAMLConfigNode(LeafNode):
    """
    M111 - YAML Configuration Leaf Node

    Responsibility: Handle all YAML configuration file I/O
    External Interface: File system (YAML files)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M111",
            name="YAML Config Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M110",
            token_budget=5000,
            metadata={"interface": "yaml_file", "file_types": [".yaml", ".yml"]}
        )
        super().__init__(config)
        self._interface_type = "yaml_file"
        self._interface: Optional[MockYAMLInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to file system interface."""
        self._interface = MockYAMLInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from file system."""
        self._interface = None
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process configuration request.

        Input format:
        {
            "action": "read" | "write",
            "path": "config/settings.yaml",
            "data": {...}  # Only for write
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 10  # Base token cost

        action = input_data.get("action", "read")
        path = input_data.get("path", "config/settings.yaml")

        try:
            if action == "read":
                result = self._interface.read(path)
                tokens_used += result.bytes_transferred // 100
            elif action == "write":
                data = input_data.get("data", {})
                result = self._interface.write(path, data)
                tokens_used += result.bytes_transferred // 50
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

    def load_config(self, path: str = "config/settings.yaml") -> Dict[str, Any]:
        """Convenience method to load configuration."""
        result = self.process({"action": "read", "path": path})
        return result.data if result.success else {}

    def save_config(self, config: Dict[str, Any], path: str = "config/settings.yaml") -> bool:
        """Convenience method to save configuration."""
        result = self.process({"action": "write", "path": path, "data": config})
        return result.success


# Factory function
def create_node() -> YAMLConfigNode:
    """Create and return M111 node instance."""
    return YAMLConfigNode()
