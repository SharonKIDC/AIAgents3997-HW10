"""
M100 - Infrastructure Manager
Level 1 Internal Node: Infrastructure Coordination

Children:
- M110 (Config Handler) - Left child
- M120 (Database Handler) - Right child

Responsibility: Coordinate infrastructure layer (config, logging, data persistence)
"""
from typing import Any, Dict, List
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M110.src.main import create_node as create_m110
from tree.M120.src.main import create_node as create_m120


class InfrastructureManagerNode(InternalNode):
    """
    M100 - Infrastructure Manager Internal Node

    Responsibility: Coordinate all infrastructure operations
    Children: M110 (Config Handler), M120 (Database Handler)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M100",
            name="Infrastructure Manager",
            level=NodeLevel.LEVEL_1,
            node_type=NodeType.MANAGER,
            parent_id="M000",
            left_child_id="M110",
            right_child_id="M120",
            token_budget=35000,
            metadata={"role": "infrastructure_management"}
        )
        super().__init__(config)
        self._system_initialized = False
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m110()  # Config Handler
        self.right = create_m120()  # Database Handler
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process infrastructure request by coordinating children.

        Input format:
        {
            "action": "initialize" | "get_tenant_data" | "save_tenant" | "system_status" | "config_update",
            "config_path": "config/settings.yaml",
            "data": {...}
        }
        """
        action = input_data.get("action", "system_status")
        tokens_used = 20

        try:
            if action == "initialize":
                # Initialize the infrastructure layer
                config_path = input_data.get("config_path", "config/settings.yaml")

                # Load configuration via M110
                config_result = self.left.process({
                    "action": "init_system",
                    "config_path": config_path
                })

                if not config_result.success:
                    return NodeResult(
                        success=False,
                        error=f"Configuration initialization failed: {config_result.error}",
                        tokens_used=tokens_used + config_result.tokens_used,
                        node_id=self.node_id
                    )

                # Verify database connection via M120
                db_result = self.right.process({
                    "action": "get_tenants",
                    "source": "database"
                })

                tokens_used += config_result.tokens_used + db_result.tokens_used

                # Log initialization result
                self.left.process({
                    "action": "log",
                    "log_level": "INFO",
                    "message": f"Infrastructure initialized. DB status: {db_result.success}"
                })

                self._system_initialized = db_result.success

                return NodeResult(
                    success=self._system_initialized,
                    data={
                        "config": config_result.data,
                        "database_connected": db_result.success,
                        "tenant_count": len(db_result.data) if db_result.success else 0
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "get_tenant_data":
                # Get tenant data with optional config
                tenant_id = input_data.get("tenant_id")
                source = input_data.get("source", "database")
                include_config = input_data.get("include_config", False)

                results = {}

                # Get tenant data from M120
                if tenant_id:
                    db_result = self.right.process({
                        "action": "query",
                        "sql": "SELECT * FROM tenants WHERE id = :id",
                        "params": {"id": tenant_id}
                    })
                else:
                    db_result = self.right.process({
                        "action": "get_tenants",
                        "source": source
                    })

                results["tenants"] = db_result.data if db_result.success else []
                tokens_used += db_result.tokens_used

                # Optionally include configuration
                if include_config:
                    config_result = self.left.process({"action": "load_config"})
                    results["config"] = config_result.data if config_result.success else {}
                    tokens_used += config_result.tokens_used

                return NodeResult(
                    success=db_result.success,
                    data=results,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "save_tenant":
                # Save tenant data and log the operation
                tenant_data = input_data.get("data", {})
                sync_excel = input_data.get("sync_excel", True)

                # Save via M120
                db_result = self.right.process({
                    "action": "add_tenant",
                    "data": tenant_data,
                    "sync_excel": sync_excel
                })

                # Log the operation via M110
                self.left.process({
                    "action": "log",
                    "log_level": "INFO" if db_result.success else "ERROR",
                    "message": f"Tenant save {'succeeded' if db_result.success else 'failed'}: {tenant_data.get('name', 'Unknown')}"
                })

                tokens_used += db_result.tokens_used + 10

                return NodeResult(
                    success=db_result.success,
                    data=db_result.data,
                    error=db_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "config_update":
                # Update configuration
                config_data = input_data.get("data", {})
                config_path = input_data.get("config_path", "config/settings.yaml")

                config_result = self.left.process({
                    "action": "save_config",
                    "config_path": config_path,
                    "data": config_data
                })

                tokens_used += config_result.tokens_used

                return NodeResult(
                    success=config_result.success,
                    data=config_result.data,
                    error=config_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "system_status":
                # Get overall system status
                status = {
                    "initialized": self._system_initialized,
                    "config_handler": self.left.get_status(),
                    "database_handler": self.right.get_status()
                }

                return NodeResult(
                    success=True,
                    data=status,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "sync_data":
                # Synchronize Excel and Database
                sync_result = self.right.process({"action": "sync"})

                self.left.process({
                    "action": "log",
                    "log_level": "INFO",
                    "message": f"Data sync completed: {sync_result.data}"
                })

                tokens_used += sync_result.tokens_used + 5

                return NodeResult(
                    success=sync_result.success,
                    data=sync_result.data,
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
            self.left.process({
                "action": "log",
                "log_level": "ERROR",
                "message": f"Infrastructure error: {str(e)}"
            })
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def initialize(self, config_path: str = "config/settings.yaml") -> bool:
        """Convenience method to initialize infrastructure."""
        result = self.process({"action": "initialize", "config_path": config_path})
        return result.success

    def get_tenants(self, source: str = "database") -> List[Dict]:
        """Convenience method to get all tenants."""
        result = self.process({
            "action": "get_tenant_data",
            "source": source
        })
        return result.data.get("tenants", []) if result.success else []


# Factory function
def create_node() -> InfrastructureManagerNode:
    """Create and return M100 node instance."""
    return InfrastructureManagerNode()
