"""
Unit tests for M000 - Root Orchestrator Node

Tests cover:
- System initialization
- Token distribution
- Workflow execution
- Tree coordination
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tree.M000.src.main import RootOrchestratorNode, create_node, build_tree


class TestRootOrchestratorNode:
    """Test suite for RootOrchestratorNode (M000)."""

    def test_node_creation(self):
        """Test root node factory and initialization."""
        node = create_node()

        assert node.node_id == "M000"
        assert not node.is_leaf
        assert node.config.level.name == "ROOT"

    def test_tree_structure(self):
        """Test that tree is properly built."""
        node = create_node()

        # Check Level 1 children
        assert node.left is not None
        assert node.right is not None
        assert node.left.node_id == "M100"
        assert node.right.node_id == "M200"

        # Check Level 2
        assert node.left.left is not None  # M110
        assert node.left.right is not None  # M120
        assert node.right.left is not None  # M210
        assert node.right.right is not None  # M220

    def test_build_tree_utility(self):
        """Test build_tree utility function."""
        tree = build_tree(total_budget=50000)

        assert tree.node_id == "M000"
        assert tree._token_balancer.total_budget == 50000

    def test_collect_all_leaves(self):
        """Test collecting all leaf nodes."""
        node = create_node()

        leaves = node._collect_all_leaves()

        assert len(leaves) == 8
        leaf_ids = {leaf.node_id for leaf in leaves}
        expected_ids = {"M111", "M112", "M121", "M122", "M211", "M212", "M221", "M222"}
        assert leaf_ids == expected_ids

    def test_process_initialize(self):
        """Test system initialization."""
        node = create_node()

        result = node.process({"action": "initialize"})

        assert result.success
        assert "infrastructure" in result.data
        assert "token_allocations" in result.data
        assert result.data["system_ready"]

    def test_process_status(self):
        """Test status query."""
        node = create_node()

        result = node.process({"action": "status"})

        assert result.success
        assert "tree_structure" in result.data
        assert result.data["tree_structure"]["total_nodes"] == 15
        assert result.data["tree_structure"]["levels"] == 4

    def test_process_route_request_m100(self):
        """Test routing request to M100 subtree."""
        node = create_node()

        result = node.process({
            "action": "route_request",
            "target": "M100",
            "request": {"action": "system_status"}
        })

        assert result.success

    def test_process_route_request_m200(self):
        """Test routing request to M200 subtree."""
        node = create_node()

        result = node.process({
            "action": "route_request",
            "target": "M200",
            "request": {"action": "status"}
        })

        assert result.success

    def test_process_rebalance(self):
        """Test token rebalancing."""
        node = create_node()

        result = node.process({
            "action": "rebalance",
            "type": "full"
        })

        assert result.success
        assert "allocations" in result.data
        assert len(result.data["allocations"]) == 8

    def test_process_full_workflow(self):
        """Test full workflow execution."""
        node = create_node()

        result = node.process({
            "action": "full_workflow",
            "workflow_type": "tenant_report",
            "data": {"id": 1, "name": "Test Tenant"}
        })

        assert result.success
        assert "workflow_id" in result.data
        assert result.data["steps_completed"] == 4

    def test_process_full_pipeline(self):
        """Test full pipeline execution (Scenario 10)."""
        node = create_node()

        result = node.process({
            "action": "full_workflow",
            "workflow_type": "full_pipeline",
            "data": {"tenant_id": 1}
        })

        assert result.success
        assert "pipeline_steps" in result.data

    def test_process_get_capabilities(self):
        """Test getting system capabilities."""
        node = create_node()

        result = node.process({"action": "get_capabilities"})

        assert result.success
        assert "infrastructure_actions" in result.data
        assert "system_actions" in result.data

    def test_convenience_initialize_system(self):
        """Test convenience initialization method."""
        node = create_node()

        success = node.initialize_system()

        assert success

    def test_convenience_get_status(self):
        """Test convenience status method."""
        node = create_node()

        status = node.get_system_status()

        assert isinstance(status, dict)
        assert "tree_structure" in status

    def test_convenience_run_workflow(self):
        """Test convenience workflow method."""
        node = create_node()

        result = node.run_workflow("tenant_report", {"id": 1})

        assert isinstance(result, dict)
        assert "workflow_id" in result

    def test_workflow_history_tracking(self):
        """Test that workflows are tracked in history."""
        node = create_node()

        node.run_workflow("tenant_report", {"id": 1})
        node.run_workflow("tenant_report", {"id": 2})

        assert len(node._workflow_history) == 2

    def test_get_node_by_path(self):
        """Test getting a node by path."""
        node = create_node()

        # Get M111 via path
        m111 = node._get_node_by_path("M100.M110.M111")

        assert m111 is not None
        assert m111.node_id == "M111"

    def test_unknown_action(self):
        """Test handling of unknown action."""
        node = create_node()

        result = node.process({"action": "invalid"})

        assert not result.success
        assert "Unknown action" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
