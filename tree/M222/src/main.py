"""
M222 - PDF Generator Handler
Leaf Node: External Interface - File I/O (PDF output)

Maps to HW8: pdf_generator.py, reporter.py
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType, NodeResult
from shared.interfaces import FileInterface, InterfaceResult


class ReportType(Enum):
    """Report types."""
    TENANT_STATEMENT = "tenant_statement"
    PAYMENT_HISTORY = "payment_history"
    BALANCE_SUMMARY = "balance_summary"
    MONTHLY_REPORT = "monthly_report"
    ANNUAL_REPORT = "annual_report"


@dataclass
class PDFDocument:
    """PDF document representation."""
    filename: str
    title: str
    content: List[Dict]
    metadata: Dict[str, Any]
    pages: int = 1
    size_bytes: int = 0


class MockPDFInterface(FileInterface):
    """Mock PDF file interface for testing."""

    def __init__(self):
        self._documents: Dict[str, PDFDocument] = {}

    def read(self, path: str) -> InterfaceResult:
        """Read PDF metadata (content reading simulated)."""
        if path not in self._documents:
            return InterfaceResult(
                success=False,
                error=f"PDF not found: {path}"
            )

        doc = self._documents[path]
        return InterfaceResult(
            success=True,
            data={
                "filename": doc.filename,
                "title": doc.title,
                "pages": doc.pages,
                "size": doc.size_bytes,
                "metadata": doc.metadata
            },
            bytes_transferred=doc.size_bytes
        )

    def write(self, path: str, data: Any) -> InterfaceResult:
        """Generate PDF document."""
        doc_data = data if isinstance(data, dict) else {"content": data}

        # Simulate PDF generation
        content = doc_data.get("content", [])
        pages = max(1, len(content) // 3)
        size_bytes = len(str(content)) * 2  # Rough estimate

        doc = PDFDocument(
            filename=path,
            title=doc_data.get("title", "Report"),
            content=content if isinstance(content, list) else [content],
            metadata={
                "created": datetime.now().isoformat(),
                "author": "Tenant Manager System",
                "report_type": doc_data.get("report_type", "general")
            },
            pages=pages,
            size_bytes=size_bytes
        )

        self._documents[path] = doc

        return InterfaceResult(
            success=True,
            data={
                "path": path,
                "pages": pages,
                "size": size_bytes,
                "created": True
            },
            bytes_transferred=size_bytes
        )

    def exists(self, path: str) -> bool:
        """Check if PDF exists."""
        return path in self._documents

    def list_documents(self) -> List[str]:
        """List all generated PDFs."""
        return list(self._documents.keys())


class PDFGeneratorNode(LeafNode):
    """
    M222 - PDF Generator Leaf Node

    Responsibility: Generate PDF reports and documents
    External Interface: File system (PDF files)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M222",
            name="PDF Generator Handler",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M220",
            token_budget=10000,
            metadata={"interface": "pdf_file", "file_types": [".pdf"]}
        )
        super().__init__(config)
        self._interface_type = "pdf_file"
        self._interface: Optional[MockPDFInterface] = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to PDF interface."""
        self._interface = MockPDFInterface()
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from PDF interface."""
        self._interface = None
        self._connected = False

    def _generate_tenant_statement(self, tenant: Dict) -> List[Dict]:
        """Generate content for tenant statement."""
        return [
            {"type": "header", "text": f"Tenant Statement - {tenant.get('name', 'Unknown')}"},
            {"type": "info", "label": "Unit", "value": tenant.get("unit", "N/A")},
            {"type": "info", "label": "Monthly Rent", "value": f"${tenant.get('rent', 0):,.2f}"},
            {"type": "info", "label": "Current Balance", "value": f"${tenant.get('balance', 0):,.2f}"},
            {"type": "footer", "text": f"Generated on {datetime.now().strftime('%Y-%m-%d')}"}
        ]

    def _generate_payment_history(self, payments: List[Dict]) -> List[Dict]:
        """Generate content for payment history."""
        content = [{"type": "header", "text": "Payment History Report"}]

        total = 0
        for payment in payments:
            content.append({
                "type": "row",
                "date": payment.get("date", "N/A"),
                "amount": f"${payment.get('amount', 0):,.2f}",
                "method": payment.get("method", "N/A")
            })
            total += payment.get("amount", 0)

        content.append({"type": "summary", "total": f"${total:,.2f}", "count": len(payments)})
        return content

    def _generate_balance_summary(self, tenants: List[Dict]) -> List[Dict]:
        """Generate content for balance summary."""
        content = [{"type": "header", "text": "Building Balance Summary"}]

        total_rent = 0
        total_balance = 0
        for tenant in tenants:
            content.append({
                "type": "row",
                "name": tenant.get("name", "Unknown"),
                "unit": tenant.get("unit", "N/A"),
                "balance": f"${tenant.get('balance', 0):,.2f}"
            })
            total_rent += tenant.get("rent", 0)
            total_balance += tenant.get("balance", 0)

        content.append({
            "type": "summary",
            "total_units": len(tenants),
            "total_monthly_rent": f"${total_rent:,.2f}",
            "total_balance": f"${total_balance:,.2f}"
        })
        return content

    def process(self, input_data: Any) -> NodeResult:
        """
        Process PDF generation request.

        Input format:
        {
            "action": "generate" | "read" | "list",
            "report_type": "tenant_statement" | "payment_history" | "balance_summary",
            "data": {...},  # Report-specific data
            "output_path": "reports/statement.pdf"
        }
        """
        if not self._connected:
            self.connect()

        tokens_used = 40  # Base token cost for PDF operations

        action = input_data.get("action", "generate")

        try:
            if action == "generate":
                report_type = input_data.get("report_type", "general")
                data = input_data.get("data", {})
                output_path = input_data.get("output_path", f"reports/{report_type}_{datetime.now().strftime('%Y%m%d')}.pdf")

                # Generate content based on report type
                if report_type == "tenant_statement":
                    content = self._generate_tenant_statement(data)
                elif report_type == "payment_history":
                    content = self._generate_payment_history(data.get("payments", []))
                elif report_type == "balance_summary":
                    content = self._generate_balance_summary(data.get("tenants", []))
                else:
                    content = [{"type": "text", "content": str(data)}]

                result = self._interface.write(output_path, {
                    "title": f"{report_type.replace('_', ' ').title()} Report",
                    "content": content,
                    "report_type": report_type
                })
                tokens_used += result.bytes_transferred // 10

            elif action == "read":
                path = input_data.get("path", "")
                result = self._interface.read(path)
                tokens_used += result.bytes_transferred // 50 if result.success else 10

            elif action == "list":
                documents = self._interface.list_documents()
                result = InterfaceResult(
                    success=True,
                    data={"documents": documents, "count": len(documents)}
                )
                tokens_used += len(documents) * 2

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

    def generate_tenant_report(self, tenant: Dict, output_path: str = None) -> Dict:
        """Convenience method to generate tenant statement."""
        result = self.process({
            "action": "generate",
            "report_type": "tenant_statement",
            "data": tenant,
            "output_path": output_path or f"reports/tenant_{tenant.get('id', 'unknown')}.pdf"
        })
        return result.data if result.success else {}

    def generate_payment_report(self, payments: List[Dict], output_path: str = None) -> Dict:
        """Convenience method to generate payment history."""
        result = self.process({
            "action": "generate",
            "report_type": "payment_history",
            "data": {"payments": payments},
            "output_path": output_path or "reports/payment_history.pdf"
        })
        return result.data if result.success else {}


# Factory function
def create_node() -> PDFGeneratorNode:
    """Create and return M222 node instance."""
    return PDFGeneratorNode()
