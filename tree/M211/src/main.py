"""
M211 - MCP Tools Handler
Leaf Node: External Interface - External API (LLM tools)

Maps to HW8: tools.py
"""
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import APIInterface, InterfaceResult


class ToolType(Enum):
    """MCP Tool types."""
    QUERY = "query"
    MUTATION = "mutation"
    ANALYSIS = "analysis"


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    tool_type: ToolType
    parameters: Dict[str, str]
    handler: Optional[Callable] = None


class MockMCPToolsInterface(APIInterface):
    """Mock MCP Tools interface for testing."""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._init_tools()

    def _init_tools(self):
        """Initialize available MCP tools."""
        self._tools = {
            "get_tenant_info": MCPTool(
                name="get_tenant_info",
                description="Get information about a tenant",
                tool_type=ToolType.QUERY,
                parameters={"tenant_id": "int"}
            ),
            "calculate_balance": MCPTool(
                name="calculate_balance",
                description="Calculate tenant balance including fees",
                tool_type=ToolType.ANALYSIS,
                parameters={"tenant_id": "int", "include_fees": "bool"}
            ),
            "send_notification": MCPTool(
                name="send_notification",
                description="Send notification to tenant",
                tool_type=ToolType.MUTATION,
                parameters={"tenant_id": "int", "message": "str", "type": "str"}
            ),
            "generate_report": MCPTool(
                name="generate_report",
                description="Generate tenant report",
                tool_type=ToolType.ANALYSIS,
                parameters={"report_type": "str", "date_range": "str"}
            ),
            "analyze_payments": MCPTool(
                name="analyze_payments",
                description="Analyze payment patterns",
                tool_type=ToolType.ANALYSIS,
                parameters={"tenant_id": "int", "period": "str"}
            )
        }

    def call(self, endpoint: str, payload: Dict) -> InterfaceResult:
        """Call MCP tool endpoint."""
        tool_name = endpoint.replace("/tools/", "")

        if tool_name not in self._tools:
            return InterfaceResult(
                success=False,
                error=f"Tool not found: {tool_name}"
            )

        tool = self._tools[tool_name]

        # Simulate tool execution
        result_data = {
            "tool": tool_name,
            "type": tool.tool_type.value,
            "input": payload,
            "output": self._simulate_tool_output(tool_name, payload)
        }

        return InterfaceResult(
            success=True,
            data=result_data,
            bytes_transferred=len(str(result_data))
        )

    def _simulate_tool_output(self, tool_name: str, payload: Dict) -> Any:
        """Simulate tool output based on tool type."""
        if tool_name == "get_tenant_info":
            return {
                "id": payload.get("tenant_id", 1),
                "name": "Sample Tenant",
                "unit": "101",
                "status": "active"
            }
        elif tool_name == "calculate_balance":
            return {
                "balance": 1500.00,
                "fees": 50.00 if payload.get("include_fees") else 0,
                "total": 1550.00 if payload.get("include_fees") else 1500.00
            }
        elif tool_name == "send_notification":
            return {"sent": True, "method": "email", "timestamp": "2024-01-15T10:00:00Z"}
        elif tool_name == "generate_report":
            return {"report_id": "RPT-001", "format": "pdf", "pages": 5}
        elif tool_name == "analyze_payments":
            return {
                "total_payments": 5,
                "average_amount": 1500.00,
                "on_time_percentage": 95.0
            }
        return {"status": "completed"}

    def get_status(self) -> Dict[str, Any]:
        """Get API status."""
        return {
            "available": True,
            "tools_count": len(self._tools),
            "tools": list(self._tools.keys())
        }

    def list_tools(self) -> List[MCPTool]:
        """List all available tools."""
        return list(self._tools.values())


class MCPToolsNode(LeafNode):
    """
    M211 - MCP Tools Leaf Node

    Responsibility: Handle MCP tool invocations
    External Interface: External API (LLM tools)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M211",
            name="MCP Tools Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M210",
            token_budget=15000,
            metadata={"interface": "mcp_api", "protocol": "MCP"}
        )
        super().__init__(config)
        self._interface_type = "mcp_api"
        self._interface: Optional[MockMCPToolsInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to MCP API."""
        self._interface = MockMCPToolsInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from MCP API."""
        self._interface = None
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process MCP tool request.

        Input format:
        {
            "action": "call" | "list" | "status",
            "tool": "get_tenant_info",
            "params": {"tenant_id": 1}
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 50  # Base token cost for API calls

        action = input_data.get("action", "call")

        try:
            if action == "call":
                tool_name = input_data.get("tool", "")
                params = input_data.get("params", {})
                result = self._interface.call(f"/tools/{tool_name}", params)
                tokens_used += result.bytes_transferred // 10

            elif action == "list":
                tools = self._interface.list_tools()
                result = InterfaceResult(
                    success=True,
                    data=[{"name": t.name, "description": t.description, "type": t.tool_type.value} for t in tools]
                )
                tokens_used += len(tools) * 10

            elif action == "status":
                status = self._interface.get_status()
                result = InterfaceResult(success=True, data=status)
                tokens_used += 5

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

    def call_tool(self, tool_name: str, params: Dict = None) -> Any:
        """Convenience method to call a tool."""
        result = self.process({
            "action": "call",
            "tool": tool_name,
            "params": params or {}
        })
        return result.data if result.success else None

    def list_available_tools(self) -> List[Dict]:
        """Convenience method to list tools."""
        result = self.process({"action": "list"})
        return result.data if result.success else []


# Factory function
def create_node() -> MCPToolsNode:
    """Create and return M211 node instance."""
    return MCPToolsNode()
