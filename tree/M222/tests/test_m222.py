"""
Tests for M222 - PDF Generator Handler
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M222.src.main import PDFGeneratorNode, MockPDFInterface, create_node


class TestMockPDFInterface:
    """Tests for the mock PDF interface."""

    def test_write_and_read(self):
        """Test writing and reading PDF."""
        interface = MockPDFInterface()
        write_result = interface.write("test.pdf", {"title": "Test", "content": ["Page 1"]})
        assert write_result.success

        read_result = interface.read("test.pdf")
        assert read_result.success
        assert read_result.data["title"] == "Test"

    def test_read_nonexistent(self):
        """Test reading non-existent PDF."""
        interface = MockPDFInterface()
        result = interface.read("nonexistent.pdf")
        assert not result.success

    def test_exists(self):
        """Test checking if PDF exists."""
        interface = MockPDFInterface()
        assert not interface.exists("test.pdf")
        interface.write("test.pdf", {"content": []})
        assert interface.exists("test.pdf")

    def test_list_documents(self):
        """Test listing documents."""
        interface = MockPDFInterface()
        interface.write("doc1.pdf", {})
        interface.write("doc2.pdf", {})
        docs = interface.list_documents()
        assert len(docs) == 2


class TestPDFGeneratorNode:
    """Tests for the PDF Generator node."""

    def test_node_creation(self):
        """Test node is created with correct configuration."""
        node = create_node()
        assert node.node_id == "M222"
        assert node.config.name == "PDF Generator Handler"

    def test_connect_disconnect(self):
        """Test connecting and disconnecting."""
        node = create_node()
        assert node.connect()
        assert node._connected
        node.disconnect()
        assert not node._connected

    def test_process_generate_tenant_statement(self):
        """Test generating tenant statement."""
        node = create_node()
        result = node.process({
            "action": "generate",
            "report_type": "tenant_statement",
            "data": {"name": "John Doe", "unit": "101", "rent": 1500, "balance": 0}
        })
        assert result.success
        assert "path" in result.data

    def test_process_generate_payment_history(self):
        """Test generating payment history."""
        node = create_node()
        result = node.process({
            "action": "generate",
            "report_type": "payment_history",
            "data": {
                "payments": [
                    {"date": "2024-01-01", "amount": 1500, "method": "check"},
                    {"date": "2024-02-01", "amount": 1500, "method": "check"}
                ]
            }
        })
        assert result.success

    def test_process_generate_balance_summary(self):
        """Test generating balance summary."""
        node = create_node()
        result = node.process({
            "action": "generate",
            "report_type": "balance_summary",
            "data": {
                "tenants": [
                    {"name": "John", "unit": "101", "balance": 0, "rent": 1500},
                    {"name": "Jane", "unit": "102", "balance": 100, "rent": 1600}
                ]
            }
        })
        assert result.success

    def test_process_list(self):
        """Test listing generated documents."""
        node = create_node()
        # Generate a document first
        node.process({
            "action": "generate",
            "report_type": "general",
            "data": {}
        })
        result = node.process({"action": "list"})
        assert result.success
        assert "documents" in result.data

    def test_process_read(self):
        """Test reading generated PDF."""
        node = create_node()
        # Generate first
        gen_result = node.process({
            "action": "generate",
            "report_type": "general",
            "output_path": "test_read.pdf"
        })
        # Then read
        result = node.process({
            "action": "read",
            "path": "test_read.pdf"
        })
        assert result.success

    def test_process_unknown_action(self):
        """Test handling unknown action."""
        node = create_node()
        result = node.process({"action": "unknown"})
        assert not result.success
        assert "Unknown action" in result.error

    def test_convenience_generate_tenant_report(self):
        """Test convenience generate_tenant_report method."""
        node = create_node()
        result = node.generate_tenant_report({"id": 1, "name": "Test", "unit": "101"})
        assert isinstance(result, dict)

    def test_convenience_generate_payment_report(self):
        """Test convenience generate_payment_report method."""
        node = create_node()
        result = node.generate_payment_report([{"amount": 1500}])
        assert isinstance(result, dict)

    def test_token_tracking(self):
        """Test that tokens are tracked."""
        node = create_node()
        result = node.process({
            "action": "generate",
            "report_type": "general",
            "data": {}
        })
        assert result.tokens_used > 0
        assert result.node_id == "M222"
