"""
M000 - Root Orchestrator
Level 0 Root Node: System-wide Coordination

Children:
- M100 (Infrastructure Manager) - Left child
- M200 (Application Manager) - Right child

Responsibility: Orchestrate entire BST, manage token distribution, coordinate workflows
"""
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult, BSTNode
from shared.utils import TokenBalancer

# Import child node factories
from tree.M100.src.main import create_node as create_m100
from tree.M200.src.main import create_node as create_m200


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    name: str
    node_path: str  # e.g., "M100.M110.M111"
    action: str
    params: Dict
    depends_on: Optional[str] = None


class RootOrchestratorNode(InternalNode):
    """
    M000 - Root Orchestrator Node

    Responsibility: System-wide orchestration and token management
    Children: M100 (Infrastructure Manager), M200 (Application Manager)

    This is the root of the Binary Spanning Tree (BST) architecture.
    It manages token distribution across all 15 nodes and coordinates
    complex workflows that span multiple subtrees.
    """

    def __init__(self, total_token_budget: int = 100000):
        config = NodeConfig(
            node_id="M000",
            name="Root Orchestrator",
            level=NodeLevel.ROOT,
            node_type=NodeType.ORCHESTRATOR,
            parent_id=None,
            left_child_id="M100",
            right_child_id="M200",
            token_budget=total_token_budget,
            metadata={
                "role": "root_orchestration",
                "tree_levels": 4,
                "total_nodes": 15
            }
        )
        super().__init__(config)

        self._token_balancer = TokenBalancer(total_token_budget)
        self._workflow_history: List[Dict] = []
        self._system_start_time = datetime.now()
        self._init_children()

    def _init_children(self):
        """Initialize child nodes and build tree."""
        self.left = create_m100()   # Infrastructure Manager
        self.right = create_m200()  # Application Manager
        self.left.parent = self
        self.right.parent = self

        # Initial token distribution
        self._distribute_tokens()

    def _distribute_tokens(self) -> Dict[str, int]:
        """
        Distribute tokens across all leaf nodes using the TokenBalancer.

        This implements the load balancing algorithm described in the plan:
        - O(1) for token queries
        - O(log n) for single leaf balance
        - O(n²) for full rebalance
        """
        return self._token_balancer.balance_tokens(self)

    def _collect_all_leaves(self, node: BSTNode = None) -> List[BSTNode]:
        """Collect all leaf nodes in the tree."""
        if node is None:
            node = self

        leaves = []
        if node.is_leaf:
            leaves.append(node)
        else:
            if hasattr(node, 'left') and node.left:
                leaves.extend(self._collect_all_leaves(node.left))
            if hasattr(node, 'right') and node.right:
                leaves.extend(self._collect_all_leaves(node.right))
        return leaves

    def _get_node_by_path(self, path: str) -> Optional[BSTNode]:
        """
        Get a node by its path (e.g., "M100.M110.M111").

        Time Complexity: O(log n) - tree depth traversal
        """
        parts = path.split(".")
        current = self

        for part in parts:
            if part == self.node_id:
                continue
            if hasattr(current, 'left') and current.left and current.left.node_id == part:
                current = current.left
            elif hasattr(current, 'right') and current.right and current.right.node_id == part:
                current = current.right
            else:
                return None
        return current

    def process(self, input_data: Any) -> NodeResult:
        """
        Process system-wide request by coordinating the entire tree.

        Input format:
        {
            "action": "initialize" | "full_workflow" | "route_request" | "status" | "rebalance",
            "workflow": [...],  # For full_workflow
            "target": "M100" | "M200",  # For route_request
            "request": {...}
        }
        """
        action = input_data.get("action", "status")
        tokens_used = 30

        try:
            if action == "initialize":
                # Initialize the entire system
                # First, initialize infrastructure (M100)
                infra_result = self.left.process({
                    "action": "initialize",
                    "config_path": input_data.get("config_path", "config/settings.yaml")
                })

                if not infra_result.success:
                    return NodeResult(
                        success=False,
                        error=f"Infrastructure initialization failed: {infra_result.error}",
                        tokens_used=tokens_used + infra_result.tokens_used,
                        node_id=self.node_id
                    )

                # Check application layer status (M200)
                app_result = self.right.process({"action": "status"})

                tokens_used += infra_result.tokens_used + app_result.tokens_used

                # Distribute tokens based on initialization
                allocations = self._distribute_tokens()

                return NodeResult(
                    success=True,
                    data={
                        "infrastructure": infra_result.data,
                        "application": app_result.data,
                        "token_allocations": allocations,
                        "system_ready": True
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "full_workflow":
                # Execute a multi-step workflow across the tree
                # Example: Config → Query → Process → Output pipeline
                workflow_type = input_data.get("workflow_type", "tenant_report")
                workflow_data = input_data.get("data", {})

                if workflow_type == "tenant_report":
                    return self._execute_tenant_report_workflow(workflow_data)
                elif workflow_type == "data_sync":
                    return self._execute_data_sync_workflow()
                elif workflow_type == "full_pipeline":
                    return self._execute_full_pipeline(workflow_data)
                else:
                    return NodeResult(
                        success=False,
                        error=f"Unknown workflow type: {workflow_type}",
                        tokens_used=tokens_used,
                        node_id=self.node_id
                    )

            elif action == "route_request":
                # Route a request to the appropriate subtree
                target = input_data.get("target", "M100")
                request = input_data.get("request", {})

                if target.startswith("M1"):
                    result = self.left.process(request)
                elif target.startswith("M2"):
                    result = self.right.process(request)
                else:
                    return NodeResult(
                        success=False,
                        error=f"Unknown target: {target}",
                        tokens_used=tokens_used,
                        node_id=self.node_id
                    )

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "rebalance":
                # Rebalance token distribution
                rebalance_type = input_data.get("type", "full")

                if rebalance_type == "full":
                    allocations = self._token_balancer.rebalance_full(self)
                else:
                    # Partial rebalance for a subtree
                    target = input_data.get("target")
                    target_node = self._get_node_by_path(target) if target else self
                    allocations = self._token_balancer.rebalance_partial(target_node)

                return NodeResult(
                    success=True,
                    data={
                        "rebalance_type": rebalance_type,
                        "allocations": allocations,
                        "utilization": self._token_balancer.get_utilization_report()
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "status":
                # Get full system status
                infra_status = self.left.process({"action": "system_status"})
                app_status = self.right.process({"action": "status"})

                tokens_used += infra_status.tokens_used + app_status.tokens_used

                leaves = self._collect_all_leaves()
                leaf_status = {leaf.node_id: leaf.get_status() for leaf in leaves}

                return NodeResult(
                    success=True,
                    data={
                        "system_uptime": str(datetime.now() - self._system_start_time),
                        "tree_structure": {
                            "total_nodes": 15,
                            "levels": 4,
                            "leaves": len(leaves)
                        },
                        "infrastructure": infra_status.data if infra_status.success else {},
                        "application": app_status.data if app_status.success else {},
                        "token_utilization": self._token_balancer.get_utilization_report(),
                        "leaf_nodes": leaf_status,
                        "workflow_count": len(self._workflow_history)
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "get_capabilities":
                # List all system capabilities
                app_caps = self.right.process({"action": "capabilities"})
                tokens_used += app_caps.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "infrastructure_actions": [
                            "initialize", "get_tenant_data", "save_tenant",
                            "config_update", "sync_data"
                        ],
                        "application_actions": app_caps.data if app_caps.success else {},
                        "system_actions": [
                            "initialize", "full_workflow", "route_request",
                            "rebalance", "status", "get_capabilities"
                        ]
                    },
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
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def _execute_tenant_report_workflow(self, data: Dict) -> NodeResult:
        """
        Execute the full tenant report workflow.

        Workflow: M111 (config) → M122 (query) → M211 (process) → M222 (output)
        """
        tokens_used = 50
        workflow_id = f"WF-{len(self._workflow_history) + 1:04d}"

        # Step 1: Load configuration (M100 → M110 → M111)
        config_result = self.left.process({
            "action": "get_tenant_data",
            "include_config": True
        })
        tokens_used += config_result.tokens_used

        # Step 2: Get tenant data (already done in step 1)
        tenant_data = data if data else {}
        if config_result.success:
            tenant_data = {**tenant_data, **config_result.data.get("tenants", [{}])[0]}

        # Step 3: Process with MCP tool (M200 → M210 → M211)
        tool_result = self.right.process({
            "action": "execute_tool",
            "tool": "get_tenant_info",
            "params": {"tenant_id": tenant_data.get("id", 1)}
        })
        tokens_used += tool_result.tokens_used

        if tool_result.success:
            tenant_data["processed"] = tool_result.data

        # Step 4: Generate PDF report (M200 → M220 → M222)
        report_result = self.right.process({
            "action": "generate_report",
            "report_type": "tenant_statement",
            "data": tenant_data
        })
        tokens_used += report_result.tokens_used

        # Record workflow
        self._workflow_history.append({
            "id": workflow_id,
            "type": "tenant_report",
            "timestamp": datetime.now().isoformat(),
            "success": report_result.success,
            "tokens_used": tokens_used
        })

        return NodeResult(
            success=report_result.success,
            data={
                "workflow_id": workflow_id,
                "steps_completed": 4,
                "config": config_result.data if config_result.success else None,
                "processing": tool_result.data if tool_result.success else None,
                "report": report_result.data if report_result.success else None
            },
            tokens_used=tokens_used,
            node_id=self.node_id
        )

    def _execute_data_sync_workflow(self) -> NodeResult:
        """Execute data synchronization workflow."""
        tokens_used = 30

        # Sync via Infrastructure Manager
        sync_result = self.left.process({"action": "sync_data"})
        tokens_used += sync_result.tokens_used

        return NodeResult(
            success=sync_result.success,
            data=sync_result.data,
            tokens_used=tokens_used,
            node_id=self.node_id
        )

    def _execute_full_pipeline(self, data: Dict) -> NodeResult:
        """
        Execute full system pipeline (Scenario 10).

        1. M111 reads YAML config
        2. M122 queries database
        3. M211 processes with MCP tool
        4. M222 generates PDF output
        """
        tokens_used = 100
        pipeline_results = []

        # Step 1: Config load via M100
        config_result = self.left.process({
            "action": "get_tenant_data",
            "include_config": True
        })
        pipeline_results.append(("config_load", config_result.success))
        tokens_used += config_result.tokens_used

        # Step 2: Already included in config_result

        # Step 3: MCP processing via M200
        process_result = self.right.process({
            "action": "execute_tool",
            "tool": "analyze_payments",
            "params": {"tenant_id": data.get("tenant_id", 1), "period": "monthly"}
        })
        pipeline_results.append(("mcp_process", process_result.success))
        tokens_used += process_result.tokens_used

        # Step 4: PDF generation via M200
        pdf_result = self.right.process({
            "action": "generate_report",
            "report_type": "payment_history",
            "data": {"payments": [{"amount": 1500, "date": "2024-01-01", "method": "check"}]}
        })
        pipeline_results.append(("pdf_generate", pdf_result.success))
        tokens_used += pdf_result.tokens_used

        all_success = all(success for _, success in pipeline_results)

        return NodeResult(
            success=all_success,
            data={
                "pipeline_steps": pipeline_results,
                "config": config_result.data if config_result.success else None,
                "analysis": process_result.data if process_result.success else None,
                "report": pdf_result.data if pdf_result.success else None
            },
            tokens_used=tokens_used,
            node_id=self.node_id
        )

    # Convenience methods
    def initialize_system(self, config_path: str = "config/settings.yaml") -> bool:
        """Initialize the entire system."""
        result = self.process({"action": "initialize", "config_path": config_path})
        return result.success

    def get_system_status(self) -> Dict:
        """Get full system status."""
        result = self.process({"action": "status"})
        return result.data if result.success else {}

    def run_workflow(self, workflow_type: str, data: Dict = None) -> Dict:
        """Run a predefined workflow."""
        result = self.process({
            "action": "full_workflow",
            "workflow_type": workflow_type,
            "data": data or {}
        })
        return result.data if result.success else {}


# Factory function
def create_node(total_budget: int = 100000) -> RootOrchestratorNode:
    """Create and return M000 root node instance."""
    return RootOrchestratorNode(total_budget)


# Tree builder utility
def build_tree(total_budget: int = 100000) -> RootOrchestratorNode:
    """Build and return the complete BST tree."""
    return create_node(total_budget)
