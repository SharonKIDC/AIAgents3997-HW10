"""
M110 - Config Handler
Level 2 Internal Node: Configuration Management

Children:
- M111 (YAML Config) - Left child
- M112 (Log Writer) - Right child

Responsibility: Coordinate configuration and logging operations
"""
from typing import Any, Dict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M111.src.main import create_node as create_m111
from tree.M112.src.main import create_node as create_m112


class ConfigHandlerNode(InternalNode):
    """
    M110 - Config Handler Internal Node

    Responsibility: Coordinate configuration loading and logging
    Children: M111 (YAML Config), M112 (Log Writer)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M110",
            name="Config Handler",
            level=NodeLevel.LEVEL_2,
            node_type=NodeType.HANDLER,
            parent_id="M100",
            left_child_id="M111",
            right_child_id="M112",
            token_budget=10000,
            metadata={"role": "config_coordination"}
        )
        super().__init__(config)
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m111()  # YAML Config
        self.right = create_m112()  # Log Writer
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process configuration request by coordinating children.

        Input format:
        {
            "action": "load_config" | "save_config" | "log" | "init_system",
            "config_path": "config/settings.yaml",
            "log_level": "INFO",
            "message": "System initialized",
            "data": {...}
        }
        """
        action = input_data.get("action", "load_config")
        tokens_used = 5

        try:
            if action == "load_config":
                # Use M111 to load configuration
                config_path = input_data.get("config_path", "config/settings.yaml")
                config_result = self.left.process({
                    "action": "read",
                    "path": config_path
                })

                # Log the operation via M112
                self.right.process({
                    "action": "log",
                    "level": "INFO",
                    "message": f"Configuration loaded from {config_path}",
                    "node_id": self.node_id
                })

                tokens_used += config_result.tokens_used + 5
                return NodeResult(
                    success=config_result.success,
                    data=config_result.data,
                    error=config_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "save_config":
                # Use M111 to save configuration
                config_path = input_data.get("config_path", "config/settings.yaml")
                config_data = input_data.get("data", {})

                config_result = self.left.process({
                    "action": "write",
                    "path": config_path,
                    "data": config_data
                })

                # Log the operation
                self.right.process({
                    "action": "log",
                    "level": "INFO",
                    "message": f"Configuration saved to {config_path}",
                    "node_id": self.node_id
                })

                tokens_used += config_result.tokens_used + 5
                return NodeResult(
                    success=config_result.success,
                    data=config_result.data,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "log":
                # Directly use M112 for logging
                log_result = self.right.process({
                    "action": "log",
                    "level": input_data.get("log_level", "INFO"),
                    "message": input_data.get("message", ""),
                    "node_id": input_data.get("source_node", self.node_id)
                })

                tokens_used += log_result.tokens_used
                return NodeResult(
                    success=log_result.success,
                    data=log_result.data,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "init_system":
                # Initialize both config and logging
                config_result = self.left.process({
                    "action": "read",
                    "path": input_data.get("config_path", "config/settings.yaml")
                })

                self.right.process({
                    "action": "log",
                    "level": "INFO",
                    "message": "System initialization started",
                    "node_id": self.node_id
                })

                if config_result.success:
                    self.right.process({
                        "action": "log",
                        "level": "INFO",
                        "message": "System initialized successfully",
                        "node_id": self.node_id
                    })
                else:
                    self.right.process({
                        "action": "log",
                        "level": "ERROR",
                        "message": f"System initialization failed: {config_result.error}",
                        "node_id": self.node_id
                    })

                tokens_used += config_result.tokens_used + 15
                return NodeResult(
                    success=config_result.success,
                    data={"config": config_result.data, "initialized": config_result.success},
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            else:
                return NodeResult(
                    success=False,
                    error=f"Unknown action: {action}",
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

        except Exception as e:
            self.right.process({
                "action": "log",
                "level": "ERROR",
                "message": f"Error in M110: {str(e)}",
                "node_id": self.node_id
            })
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def get_config(self, path: str = "config/settings.yaml") -> Dict:
        """Convenience method to get configuration."""
        result = self.process({"action": "load_config", "config_path": path})
        return result.data if result.success else {}

    def log(self, level: str, message: str) -> bool:
        """Convenience method to log a message."""
        result = self.process({
            "action": "log",
            "log_level": level,
            "message": message
        })
        return result.success


# Factory function
def create_node() -> ConfigHandlerNode:
    """Create and return M110 node instance."""
    return ConfigHandlerNode()
