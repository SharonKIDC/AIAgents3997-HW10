"""
M200 - Application Manager
Level 1 Internal Node: Application Layer Coordination

Children:
- M210 (Server Handler) - Left child
- M220 (Output Handler) - Right child

Responsibility: Coordinate application layer (MCP server, outputs)
"""
from typing import Any, Dict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M210.src.main import create_node as create_m210
from tree.M220.src.main import create_node as create_m220


class ApplicationManagerNode(InternalNode):
    """
    M200 - Application Manager Internal Node

    Responsibility: Coordinate all application layer operations
    Children: M210 (Server Handler), M220 (Output Handler)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M200",
            name="Application Manager",
            level=NodeLevel.LEVEL_1,
            node_type=NodeType.MANAGER,
            parent_id="M000",
            left_child_id="M210",
            right_child_id="M220",
            token_budget=55000,
            metadata={"role": "application_management"}
        )
        super().__init__(config)
        self._server_running = False
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m210()  # Server Handler
        self.right = create_m220()  # Output Handler
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process application request by coordinating children.

        Input format:
        {
            "action": "process_request" | "generate_report" | "execute_tool" | "full_pipeline" | "status",
            "request_type": "api" | "tool" | "report",
            "tool": "get_tenant_info",
            "report_type": "tenant_statement",
            "data": {...}
        }
        """
        action = input_data.get("action", "status")
        tokens_used = 25

        try:
            if action == "process_request":
                # Route request to appropriate handler
                request_type = input_data.get("request_type", "api")

                if request_type == "api":
                    # Handle via Output Handler (M220)
                    result = self.right.process({
                        "action": "api_request",
                        "method": input_data.get("method", "GET"),
                        "url": input_data.get("url", ""),
                        "data": input_data.get("data", {})
                    })
                elif request_type == "tool":
                    # Handle via Server Handler (M210)
                    result = self.left.process({
                        "action": "call_tool",
                        "tool": input_data.get("tool", ""),
                        "params": input_data.get("params", {})
                    })
                elif request_type == "report":
                    # Handle via Output Handler (M220)
                    result = self.right.process({
                        "action": "generate_pdf",
                        "report_type": input_data.get("report_type", "general"),
                        "data": input_data.get("data", {})
                    })
                else:
                    return NodeResult(
                        success=False,
                        error=f"Unknown request type: {request_type}",
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

            elif action == "generate_report":
                # Generate a report using MCP tools and PDF generator
                report_type = input_data.get("report_type", "tenant_statement")
                tenant_data = input_data.get("data", {})

                # First, use MCP tool to process/analyze data if needed
                if input_data.get("analyze", False):
                    tool_result = self.left.process({
                        "action": "call_tool",
                        "tool": "analyze_payments" if report_type == "payment_history" else "calculate_balance",
                        "params": tenant_data
                    })
                    if tool_result.success:
                        tenant_data["analysis"] = tool_result.data
                    tokens_used += tool_result.tokens_used

                # Generate the PDF report
                pdf_result = self.right.process({
                    "action": "generate_pdf",
                    "report_type": report_type,
                    "data": tenant_data
                })

                tokens_used += pdf_result.tokens_used

                return NodeResult(
                    success=pdf_result.success,
                    data={
                        "report": pdf_result.data,
                        "analysis_included": input_data.get("analyze", False)
                    },
                    error=pdf_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "execute_tool":
                # Execute an MCP tool with optional prompt context
                tool_name = input_data.get("tool", "")
                params = input_data.get("params", {})
                use_prompt = input_data.get("use_prompt")

                if use_prompt:
                    result = self.left.process({
                        "action": "execute_with_prompt",
                        "tool": tool_name,
                        "params": params,
                        "resource": use_prompt,
                        "variables": input_data.get("prompt_variables", {})
                    })
                else:
                    result = self.left.process({
                        "action": "call_tool",
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

            elif action == "full_pipeline":
                # Execute a full application pipeline:
                # 1. Fetch data via API
                # 2. Process with MCP tool
                # 3. Generate PDF report

                tenant_id = input_data.get("tenant_id", 1)
                report_type = input_data.get("report_type", "tenant_statement")

                # Step 1: Fetch tenant data via API
                api_result = self.right.process({
                    "action": "api_request",
                    "method": "GET",
                    "url": f"/api/tenants/{tenant_id}"
                })

                if not api_result.success:
                    return NodeResult(
                        success=False,
                        error=f"API fetch failed: {api_result.error}",
                        tokens_used=tokens_used + api_result.tokens_used,
                        node_id=self.node_id
                    )

                tenant_data = api_result.data
                tokens_used += api_result.tokens_used

                # Step 2: Process with MCP tool
                tool_result = self.left.process({
                    "action": "call_tool",
                    "tool": "get_tenant_info",
                    "params": {"tenant_id": tenant_id}
                })

                if tool_result.success:
                    tenant_data = {**tenant_data, **tool_result.data.get("output", {})}
                tokens_used += tool_result.tokens_used

                # Step 3: Generate PDF report
                pdf_result = self.right.process({
                    "action": "generate_pdf",
                    "report_type": report_type,
                    "data": tenant_data
                })

                tokens_used += pdf_result.tokens_used

                return NodeResult(
                    success=pdf_result.success,
                    data={
                        "tenant_data": tenant_data,
                        "tool_analysis": tool_result.data if tool_result.success else None,
                        "pdf_report": pdf_result.data if pdf_result.success else None,
                        "pipeline_steps": ["api_fetch", "tool_process", "pdf_generate"]
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "capabilities":
                # Get all application capabilities
                server_caps = self.left.process({"action": "list_capabilities"})
                output_caps = self.right.process({"action": "list_outputs"})

                tokens_used += server_caps.tokens_used + output_caps.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "server": server_caps.data if server_caps.success else {},
                        "outputs": output_caps.data if output_caps.success else {}
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "status":
                # Get application status
                server_status = self.left.process({"action": "status"})
                tokens_used += server_status.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "application_running": True,
                        "server_handler": server_status.data if server_status.success else {},
                        "output_handler": self.right.get_status()
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
            "action": "execute_tool",
            "tool": tool_name,
            "params": params or {}
        })
        return result.data if result.success else None

    def generate_tenant_report(self, tenant_data: Dict) -> Dict:
        """Convenience method to generate a tenant report."""
        result = self.process({
            "action": "generate_report",
            "report_type": "tenant_statement",
            "data": tenant_data
        })
        return result.data if result.success else {}


# Factory function
def create_node() -> ApplicationManagerNode:
    """Create and return M200 node instance."""
    return ApplicationManagerNode()
