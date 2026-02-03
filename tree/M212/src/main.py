"""
M212 - MCP Resources Handler
Leaf Node: External Interface - External API (MCP resources)

Maps to HW8: resources.py, prompts.py
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import APIInterface, InterfaceResult


class ResourceType(Enum):
    """MCP Resource types."""
    TEMPLATE = "template"
    PROMPT = "prompt"
    SCHEMA = "schema"
    DATA = "data"


@dataclass
class MCPResource:
    """MCP Resource definition."""
    uri: str
    name: str
    resource_type: ResourceType
    description: str
    content: Any


class MockMCPResourcesInterface(APIInterface):
    """Mock MCP Resources interface for testing."""

    def __init__(self):
        self._resources: Dict[str, MCPResource] = {}
        self._init_resources()

    def _init_resources(self):
        """Initialize available MCP resources."""
        self._resources = {
            "prompt://tenant-report": MCPResource(
                uri="prompt://tenant-report",
                name="Tenant Report Prompt",
                resource_type=ResourceType.PROMPT,
                description="Prompt for generating tenant reports",
                content={
                    "template": "Generate a report for tenant {tenant_name} in unit {unit}.",
                    "variables": ["tenant_name", "unit", "period"]
                }
            ),
            "prompt://payment-reminder": MCPResource(
                uri="prompt://payment-reminder",
                name="Payment Reminder Prompt",
                resource_type=ResourceType.PROMPT,
                description="Prompt for payment reminder messages",
                content={
                    "template": "Dear {tenant_name}, your rent of ${amount} is due on {due_date}.",
                    "variables": ["tenant_name", "amount", "due_date"]
                }
            ),
            "schema://tenant": MCPResource(
                uri="schema://tenant",
                name="Tenant Schema",
                resource_type=ResourceType.SCHEMA,
                description="JSON schema for tenant data",
                content={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "unit": {"type": "string"},
                        "rent": {"type": "number"}
                    },
                    "required": ["name", "unit", "rent"]
                }
            ),
            "template://invoice": MCPResource(
                uri="template://invoice",
                name="Invoice Template",
                resource_type=ResourceType.TEMPLATE,
                description="Template for generating invoices",
                content={
                    "header": "Residential Complex Invoice",
                    "fields": ["tenant_name", "unit", "amount", "due_date", "items"],
                    "footer": "Thank you for your payment"
                }
            ),
            "data://building-info": MCPResource(
                uri="data://building-info",
                name="Building Information",
                resource_type=ResourceType.DATA,
                description="Static building information",
                content={
                    "name": "Sunset Apartments",
                    "address": "123 Main Street",
                    "units": 50,
                    "floors": 5,
                    "amenities": ["gym", "pool", "parking"]
                }
            )
        }

    def call(self, endpoint: str, payload: Dict) -> InterfaceResult:
        """Fetch MCP resource."""
        uri = payload.get("uri", endpoint)

        if uri not in self._resources:
            return InterfaceResult(
                success=False,
                error=f"Resource not found: {uri}"
            )

        resource = self._resources[uri]

        # Apply variable substitution if provided
        content = resource.content
        if "variables" in payload and isinstance(content, dict) and "template" in content:
            template = content["template"]
            for key, value in payload["variables"].items():
                template = template.replace(f"{{{key}}}", str(value))
            content = {**content, "rendered": template}

        result_data = {
            "uri": resource.uri,
            "name": resource.name,
            "type": resource.resource_type.value,
            "content": content
        }

        return InterfaceResult(
            success=True,
            data=result_data,
            bytes_transferred=len(str(result_data))
        )

    def get_status(self) -> Dict[str, Any]:
        """Get API status."""
        return {
            "available": True,
            "resources_count": len(self._resources),
            "resource_types": list(set(r.resource_type.value for r in self._resources.values()))
        }

    def list_resources(self) -> List[MCPResource]:
        """List all available resources."""
        return list(self._resources.values())


class MCPResourcesNode(LeafNode):
    """
    M212 - MCP Resources Leaf Node

    Responsibility: Handle MCP resource fetching and prompts
    External Interface: External API (MCP resources)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M212",
            name="MCP Resources Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M210",
            token_budget=8000,
            metadata={"interface": "mcp_api", "protocol": "MCP"}
        )
        super().__init__(config)
        self._interface_type = "mcp_api"
        self._interface: Optional[MockMCPResourcesInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to MCP API."""
        self._interface = MockMCPResourcesInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from MCP API."""
        self._interface = None
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process MCP resource request.

        Input format:
        {
            "action": "fetch" | "list" | "render",
            "uri": "prompt://tenant-report",
            "variables": {"tenant_name": "John"}  # For render
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 30  # Base token cost

        action = input_data.get("action", "fetch")

        try:
            if action == "fetch":
                uri = input_data.get("uri", "")
                result = self._interface.call(uri, {"uri": uri})
                tokens_used += result.bytes_transferred // 20

            elif action == "render":
                uri = input_data.get("uri", "")
                variables = input_data.get("variables", {})
                result = self._interface.call(uri, {"uri": uri, "variables": variables})
                tokens_used += result.bytes_transferred // 15

            elif action == "list":
                resources = self._interface.list_resources()
                result = InterfaceResult(
                    success=True,
                    data=[{
                        "uri": r.uri,
                        "name": r.name,
                        "type": r.resource_type.value,
                        "description": r.description
                    } for r in resources]
                )
                tokens_used += len(resources) * 5

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

    def get_prompt(self, uri: str, variables: Dict = None) -> str:
        """Convenience method to get and render a prompt."""
        result = self.process({
            "action": "render",
            "uri": uri,
            "variables": variables or {}
        })
        if result.success and result.data:
            content = result.data.get("content", {})
            return content.get("rendered", content.get("template", ""))
        return ""

    def get_schema(self, uri: str) -> Dict:
        """Convenience method to get a schema."""
        result = self.process({"action": "fetch", "uri": uri})
        return result.data.get("content", {}) if result.success else {}


# Factory function
def create_node() -> MCPResourcesNode:
    """Create and return M212 node instance."""
    return MCPResourcesNode()
