"""
M210 - Server Handler
Level 2 Internal Node: MCP Server Coordination

Children:
- M211 (MCP Tools) - Left child
- M212 (MCP Resources) - Right child

Responsibility: Coordinate MCP server tools and resources
"""
from typing import Any, Dict, List, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M211.src.main import create_node as create_m211
from tree.M212.src.main import create_node as create_m212


class ServerHandlerNode(InternalNode):
    """
    M210 - Server Handler Internal Node

    Responsibility: Coordinate MCP server operations
    Children: M211 (MCP Tools), M212 (MCP Resources)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M210",
            name="Server Handler",
            level=NodeLevel.LEVEL_2,
            node_type=NodeType.HANDLER,
            parent_id="M200",
            left_child_id="M211",
            right_child_id="M212",
            token_budget=25000,
            metadata={"role": "mcp_coordination", "protocol": "MCP"}
        )
        super().__init__(config)
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m211()  # MCP Tools
        self.right = create_m212()  # MCP Resources
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process MCP server request by coordinating children.

        Input format:
        {
            "action": "call_tool" | "get_resource" | "execute_with_prompt" | "list_capabilities",
            "tool": "get_tenant_info",
            "resource": "prompt://tenant-report",
            "params": {...},
            "variables": {...}
        }
        """
        action = input_data.get("action", "list_capabilities")
        tokens_used = 15

        try:
            if action == "call_tool":
                # Use M211 to call an MCP tool
                tool_name = input_data.get("tool", "")
                params = input_data.get("params", {})

                result = self.left.process({
                    "action": "call",
                    "tool": tool_name,
                    "params": params
                })

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "get_resource":
                # Use M212 to fetch an MCP resource
                resource_uri = input_data.get("resource", "")
                variables = input_data.get("variables", {})

                result = self.right.process({
                    "action": "render" if variables else "fetch",
                    "uri": resource_uri,
                    "variables": variables
                })

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "execute_with_prompt":
                # Get prompt from M212, then call tool from M211
                prompt_uri = input_data.get("resource", "")
                variables = input_data.get("variables", {})
                tool_name = input_data.get("tool", "")
                tool_params = input_data.get("params", {})

                # First, get the rendered prompt
                prompt_result = self.right.process({
                    "action": "render",
                    "uri": prompt_uri,
                    "variables": variables
                })

                if not prompt_result.success:
                    return NodeResult(
                        success=False,
                        error=f"Failed to get prompt: {prompt_result.error}",
                        tokens_used=tokens_used + prompt_result.tokens_used,
                        node_id=self.node_id
                    )

                # Add prompt to tool params
                enhanced_params = {
                    **tool_params,
                    "prompt_context": prompt_result.data.get("content", {})
                }

                # Call the tool with enhanced params
                tool_result = self.left.process({
                    "action": "call",
                    "tool": tool_name,
                    "params": enhanced_params
                })

                tokens_used += prompt_result.tokens_used + tool_result.tokens_used
                return NodeResult(
                    success=tool_result.success,
                    data={
                        "prompt": prompt_result.data,
                        "tool_result": tool_result.data
                    },
                    error=tool_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "list_capabilities":
                # List all available tools and resources
                tools_result = self.left.process({"action": "list"})
                resources_result = self.right.process({"action": "list"})

                tokens_used += tools_result.tokens_used + resources_result.tokens_used

                return NodeResult(
                    success=tools_result.success and resources_result.success,
                    data={
                        "tools": tools_result.data if tools_result.success else [],
                        "resources": resources_result.data if resources_result.success else []
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "status":
                # Get status of both children
                tools_status = self.left.process({"action": "status"})
                resources_status = self.right.process({"action": "status"})

                tokens_used += tools_status.tokens_used + resources_status.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "tools_status": tools_status.data,
                        "resources_status": resources_status.data,
                        "server_healthy": tools_status.success and resources_status.success
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

    def call_tool(self, tool_name: str, params: Dict = None) -> Any:
        """Convenience method to call an MCP tool."""
        result = self.process({
            "action": "call_tool",
            "tool": tool_name,
            "params": params or {}
        })
        return result.data if result.success else None

    def get_prompt(self, uri: str, variables: Dict = None) -> str:
        """Convenience method to get a rendered prompt."""
        result = self.process({
            "action": "get_resource",
            "resource": uri,
            "variables": variables or {}
        })
        if result.success and result.data:
            content = result.data.get("content", {})
            return content.get("rendered", content.get("template", ""))
        return ""


# Factory function
def create_node() -> ServerHandlerNode:
    """Create and return M210 node instance."""
    return ServerHandlerNode()
