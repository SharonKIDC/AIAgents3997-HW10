"""
M221 - Web Interface Handler
Leaf Node: External Interface - HTTP (REST API)

Maps to HW8: backend.py, routes.py, http_client.py
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import HTTPInterface, InterfaceResult


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class APIEndpoint:
    """API endpoint definition."""
    path: str
    method: HTTPMethod
    description: str
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None


class MockHTTPInterface(HTTPInterface):
    """Mock HTTP interface for testing."""

    def __init__(self):
        self._endpoints: Dict[str, APIEndpoint] = {}
        self._data_store: Dict[str, List[Dict]] = {
            "tenants": [
                {"id": 1, "name": "John Doe", "unit": "101"},
                {"id": 2, "name": "Jane Smith", "unit": "102"},
            ],
            "payments": [
                {"id": 1, "tenant_id": 1, "amount": 1500.0},
            ]
        }
        self._init_endpoints()

    def _init_endpoints(self):
        """Initialize API endpoints."""
        self._endpoints = {
            "/api/tenants": APIEndpoint("/api/tenants", HTTPMethod.GET, "List all tenants"),
            "/api/tenants/{id}": APIEndpoint("/api/tenants/{id}", HTTPMethod.GET, "Get tenant by ID"),
            "/api/payments": APIEndpoint("/api/payments", HTTPMethod.POST, "Record payment"),
            "/api/reports": APIEndpoint("/api/reports", HTTPMethod.GET, "Get reports"),
        }

    def get(self, url: str, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP GET request."""
        if "/api/tenants" in url:
            if url == "/api/tenants":
                return InterfaceResult(
                    success=True,
                    data=self._data_store["tenants"],
                    bytes_transferred=len(str(self._data_store["tenants"]))
                )
            else:
                # Extract ID from URL
                tenant_id = int(url.split("/")[-1])
                tenant = next((t for t in self._data_store["tenants"] if t["id"] == tenant_id), None)
                if tenant:
                    return InterfaceResult(success=True, data=tenant)
                return InterfaceResult(success=False, error="Tenant not found")

        elif "/api/payments" in url:
            return InterfaceResult(
                success=True,
                data=self._data_store["payments"]
            )

        elif "/api/reports" in url:
            return InterfaceResult(
                success=True,
                data={"reports": ["monthly", "quarterly", "annual"]}
            )

        return InterfaceResult(success=False, error="Endpoint not found")

    def post(self, url: str, data: Any, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP POST request."""
        if "/api/tenants" in url:
            new_id = max(t["id"] for t in self._data_store["tenants"]) + 1 if self._data_store["tenants"] else 1
            new_tenant = {"id": new_id, **data}
            self._data_store["tenants"].append(new_tenant)
            return InterfaceResult(
                success=True,
                data=new_tenant,
                bytes_transferred=len(str(new_tenant))
            )

        elif "/api/payments" in url:
            new_id = max(p["id"] for p in self._data_store["payments"]) + 1 if self._data_store["payments"] else 1
            new_payment = {"id": new_id, **data}
            self._data_store["payments"].append(new_payment)
            return InterfaceResult(
                success=True,
                data=new_payment
            )

        elif "/api/reports" in url:
            # Handle report notifications
            return InterfaceResult(
                success=True,
                data={"status": "accepted", "report_type": data.get("type", "unknown")}
            )

        return InterfaceResult(success=False, error="Endpoint not found")

    def put(self, url: str, data: Any, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP PUT request."""
        if "/api/tenants/" in url:
            tenant_id = int(url.split("/")[-1])
            for tenant in self._data_store["tenants"]:
                if tenant["id"] == tenant_id:
                    tenant.update(data)
                    return InterfaceResult(success=True, data=tenant)
            return InterfaceResult(success=False, error="Tenant not found")

        return InterfaceResult(success=False, error="Endpoint not found")

    def delete(self, url: str, headers: Optional[Dict] = None) -> InterfaceResult:
        """HTTP DELETE request."""
        if "/api/tenants/" in url:
            tenant_id = int(url.split("/")[-1])
            self._data_store["tenants"] = [t for t in self._data_store["tenants"] if t["id"] != tenant_id]
            return InterfaceResult(success=True, data={"deleted": tenant_id})

        return InterfaceResult(success=False, error="Endpoint not found")


class WebInterfaceNode(LeafNode):
    """
    M221 - Web Interface Leaf Node

    Responsibility: Handle HTTP/REST API communications
    External Interface: HTTP (REST API)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M221",
            name="Web Interface Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M220",
            token_budget=12000,
            metadata={"interface": "http", "protocol": "REST"}
        )
        super().__init__(config)
        self._interface_type = "http"
        self._interface: Optional[MockHTTPInterface] = None
        self._connected = False
        self._base_url = "http://localhost:8000"

    def connect(self) -> bool:
        """Connect to HTTP interface."""
        self._interface = MockHTTPInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from HTTP interface."""
        self._interface = None
        self._connected = False

    def process(self, input_data: Any) -> NodeResult:
        """
        Process HTTP request.

        Input format:
        {
            "method": "GET" | "POST" | "PUT" | "DELETE",
            "url": "/api/tenants",
            "data": {...},  # For POST/PUT
            "headers": {...}
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 25  # Base token cost

        method = input_data.get("method", "GET").upper()
        url = input_data.get("url", "")
        data = input_data.get("data", {})
        headers = input_data.get("headers", {})

        try:
            if method == "GET":
                result = self._interface.get(url, headers)
            elif method == "POST":
                result = self._interface.post(url, data, headers)
            elif method == "PUT":
                result = self._interface.put(url, data, headers)
            elif method == "DELETE":
                result = self._interface.delete(url, headers)
            else:
                return NodeResult(
                    success=False,
                    error=f"Unknown method: {method}",
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            tokens_used += result.bytes_transferred // 15

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

    def api_get(self, endpoint: str) -> Any:
        """Convenience method for GET request."""
        result = self.process({"method": "GET", "url": endpoint})
        return result.data if result.success else None

    def api_post(self, endpoint: str, data: Dict) -> Any:
        """Convenience method for POST request."""
        result = self.process({"method": "POST", "url": endpoint, "data": data})
        return result.data if result.success else None

    def get_tenants(self) -> List[Dict]:
        """Get all tenants via API."""
        return self.api_get("/api/tenants") or []

    def create_tenant(self, tenant_data: Dict) -> Optional[Dict]:
        """Create a new tenant via API."""
        return self.api_post("/api/tenants", tenant_data)


# Factory function
def create_node() -> WebInterfaceNode:
    """Create and return M221 node instance."""
    return WebInterfaceNode()
