"""
M220 - Output Handler
Level 2 Internal Node: Output Generation Coordination

Children:
- M221 (Web Interface) - Left child
- M222 (PDF Generator) - Right child

Responsibility: Coordinate output generation across web and PDF
"""
from typing import Any, Dict, List, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M221.src.main import create_node as create_m221
from tree.M222.src.main import create_node as create_m222


class OutputHandlerNode(InternalNode):
    """
    M220 - Output Handler Internal Node

    Responsibility: Coordinate output generation operations
    Children: M221 (Web Interface), M222 (PDF Generator)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M220",
            name="Output Handler",
            level=NodeLevel.LEVEL_2,
            node_type=NodeType.HANDLER,
            parent_id="M200",
            left_child_id="M221",
            right_child_id="M222",
            token_budget=25000,
            metadata={"role": "output_coordination"}
        )
        super().__init__(config)
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m221()  # Web Interface
        self.right = create_m222()  # PDF Generator
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process output request by coordinating children.

        Input format:
        {
            "action": "api_request" | "generate_pdf" | "fetch_and_report" | "multi_output",
            "method": "GET" | "POST",
            "url": "/api/tenants",
            "report_type": "tenant_statement",
            "data": {...}
        }
        """
        action = input_data.get("action", "api_request")
        tokens_used = 10

        try:
            if action == "api_request":
                # Use M221 for web API operations
                method = input_data.get("method", "GET")
                url = input_data.get("url", "")
                data = input_data.get("data", {})
                headers = input_data.get("headers", {})

                result = self.left.process({
                    "method": method,
                    "url": url,
                    "data": data,
                    "headers": headers
                })

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "generate_pdf":
                # Use M222 to generate PDF
                report_type = input_data.get("report_type", "general")
                report_data = input_data.get("data", {})
                output_path = input_data.get("output_path")

                result = self.right.process({
                    "action": "generate",
                    "report_type": report_type,
                    "data": report_data,
                    "output_path": output_path
                })

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "fetch_and_report":
                # Fetch data via API, then generate PDF report
                api_url = input_data.get("url", "/api/tenants")
                report_type = input_data.get("report_type", "balance_summary")

                # Fetch data from API
                api_result = self.left.process({
                    "method": "GET",
                    "url": api_url
                })

                if not api_result.success:
                    return NodeResult(
                        success=False,
                        error=f"API fetch failed: {api_result.error}",
                        tokens_used=tokens_used + api_result.tokens_used,
                        node_id=self.node_id
                    )

                # Generate PDF with fetched data
                pdf_data = api_result.data
                if report_type == "balance_summary":
                    pdf_data = {"tenants": api_result.data if isinstance(api_result.data, list) else []}
                elif report_type == "payment_history":
                    pdf_data = {"payments": api_result.data if isinstance(api_result.data, list) else []}

                pdf_result = self.right.process({
                    "action": "generate",
                    "report_type": report_type,
                    "data": pdf_data
                })

                tokens_used += api_result.tokens_used + pdf_result.tokens_used

                return NodeResult(
                    success=pdf_result.success,
                    data={
                        "api_data": api_result.data,
                        "pdf_info": pdf_result.data
                    },
                    error=pdf_result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "multi_output":
                # Generate multiple output formats simultaneously
                report_data = input_data.get("data", {})
                report_type = input_data.get("report_type", "tenant_statement")

                # Post to API (for notifications/webhooks)
                api_result = self.left.process({
                    "method": "POST",
                    "url": "/api/reports",
                    "data": {"type": report_type, "status": "generating"}
                })

                # Generate PDF
                pdf_result = self.right.process({
                    "action": "generate",
                    "report_type": report_type,
                    "data": report_data
                })

                tokens_used += api_result.tokens_used + pdf_result.tokens_used

                return NodeResult(
                    success=api_result.success and pdf_result.success,
                    data={
                        "api_notification": api_result.data,
                        "pdf_generated": pdf_result.data,
                        "outputs": ["api", "pdf"]
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "list_outputs":
                # List available documents/outputs
                pdf_list = self.right.process({"action": "list"})

                tokens_used += pdf_list.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "pdf_documents": pdf_list.data if pdf_list.success else [],
                        "api_endpoints": ["/api/tenants", "/api/payments", "/api/reports"]
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

    def api_get(self, endpoint: str) -> Any:
        """Convenience method for API GET."""
        result = self.process({
            "action": "api_request",
            "method": "GET",
            "url": endpoint
        })
        return result.data if result.success else None

    def generate_report(self, report_type: str, data: Dict) -> Dict:
        """Convenience method to generate a report."""
        result = self.process({
            "action": "generate_pdf",
            "report_type": report_type,
            "data": data
        })
        return result.data if result.success else {}


# Factory function
def create_node() -> OutputHandlerNode:
    """Create and return M220 node instance."""
    return OutputHandlerNode()
