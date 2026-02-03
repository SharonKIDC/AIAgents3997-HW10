"""
Unit tests for TokenBalancer - Load Control Algorithm

Tests cover:
- Token distribution O(log n)
- Query operations O(1)
- Rebalancing O(n²)
- Weight calculations
"""
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.token_balancer import TokenBalancer, NodeWeight, AllocationRecord


class MockNode:
    """Mock BST node for testing."""

    def __init__(self, node_id: str, is_leaf: bool = False):
        self.node_id = node_id
        self._is_leaf = is_leaf
        self.left = None
        self.right = None
        self._allocation = 0

    @property
    def is_leaf(self) -> bool:
        return self._is_leaf

    def set_allocation(self, tokens: int) -> None:
        self._allocation = tokens


def create_mock_tree():
    """Create a mock BST tree structure for testing."""
    # Root
    root = MockNode("M000", is_leaf=False)

    # Level 1
    m100 = MockNode("M100", is_leaf=False)
    m200 = MockNode("M200", is_leaf=False)
    root.left = m100
    root.right = m200

    # Level 2
    m110 = MockNode("M110", is_leaf=False)
    m120 = MockNode("M120", is_leaf=False)
    m210 = MockNode("M210", is_leaf=False)
    m220 = MockNode("M220", is_leaf=False)
    m100.left = m110
    m100.right = m120
    m200.left = m210
    m200.right = m220

    # Level 3 (Leaves)
    m111 = MockNode("M111", is_leaf=True)
    m112 = MockNode("M112", is_leaf=True)
    m121 = MockNode("M121", is_leaf=True)
    m122 = MockNode("M122", is_leaf=True)
    m211 = MockNode("M211", is_leaf=True)
    m212 = MockNode("M212", is_leaf=True)
    m221 = MockNode("M221", is_leaf=True)
    m222 = MockNode("M222", is_leaf=True)

    m110.left = m111
    m110.right = m112
    m120.left = m121
    m120.right = m122
    m210.left = m211
    m210.right = m212
    m220.left = m221
    m220.right = m222

    return root


class TestTokenBalancer:
    """Test suite for TokenBalancer."""

    def test_initialization(self):
        """Test balancer initialization."""
        balancer = TokenBalancer(total_budget=100000)
        assert balancer.total_budget == 100000
        assert len(balancer.leaf_allocations) == 0

    def test_balance_tokens_distributes_to_leaves(self):
        """Test that tokens are distributed only to leaf nodes."""
        balancer = TokenBalancer(total_budget=80000)
        tree = create_mock_tree()

        allocations = balancer.balance_tokens(tree)

        # Should have 8 leaf allocations
        assert len(allocations) == 8

        # All leaf nodes should be present
        leaf_ids = ["M111", "M112", "M121", "M122", "M211", "M212", "M221", "M222"]
        for leaf_id in leaf_ids:
            assert leaf_id in allocations

        # Total should equal budget
        assert sum(allocations.values()) == 80000

    def test_get_allocation_o1_complexity(self):
        """Test O(1) token query via hash lookup."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()
        balancer.balance_tokens(tree)

        # Query should be O(1) - direct hash lookup
        allocation = balancer.get_allocation("M111")
        assert allocation > 0

        # Non-existent node returns 0
        assert balancer.get_allocation("M999") == 0

    def test_update_weight_affects_distribution(self):
        """Test that weight updates affect token distribution."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()

        # Initial distribution
        initial = balancer.balance_tokens(tree)
        initial_m111 = initial["M111"]

        # Increase weight for M111
        balancer.update_weight("M111", historical_usage=2.0, priority=10)

        # Rebalance
        updated = balancer.balance_tokens(tree)

        # M111 should get more tokens now
        assert updated["M111"] > initial_m111

    def test_record_consumption(self):
        """Test token consumption recording."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()
        balancer.balance_tokens(tree)

        # Record consumption
        balancer.record_consumption("M111", 500)
        balancer.record_consumption("M111", 300)

        # Check utilization report
        report = balancer.get_utilization_report()
        assert report["M111"]["consumed"] == 800

    def test_utilization_report(self):
        """Test utilization report generation."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()
        balancer.balance_tokens(tree)

        # Record some consumption
        balancer.record_consumption("M111", 5000)

        report = balancer.get_utilization_report()

        assert "M111" in report
        assert "allocated" in report["M111"]
        assert "consumed" in report["M111"]
        assert "utilization" in report["M111"]
        assert "remaining" in report["M111"]

    def test_rebalance_full(self):
        """Test full rebalancing - O(n²) operation."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()
        balancer.balance_tokens(tree)

        # Record high utilization for some nodes
        balancer.record_consumption("M111", balancer.get_allocation("M111") - 100)

        # Full rebalance should recalculate all weights
        new_allocations = balancer.rebalance_full(tree)

        assert len(new_allocations) == 8
        assert sum(new_allocations.values()) == 100000

    def test_simulate_load(self):
        """Test load simulation for testing purposes."""
        balancer = TokenBalancer(total_budget=100000)
        tree = create_mock_tree()
        balancer.balance_tokens(tree)

        # Simulate load
        consumed = balancer.simulate_load("M111")

        assert consumed > 0
        report = balancer.get_utilization_report()
        assert report["M111"]["consumed"] == consumed


class TestNodeWeight:
    """Test suite for NodeWeight dataclass."""

    def test_default_weight(self):
        """Test default weight calculation."""
        weight = NodeWeight()
        assert weight.total_weight == 1.0  # 1.0 * 1.0 * 1.0 * (5/5)

    def test_custom_weight(self):
        """Test custom weight calculation."""
        weight = NodeWeight(
            historical_usage=2.0,
            queue_depth=5,
            complexity=1.5,
            priority=10
        )
        # 2.0 * 1.5 * (1 + 5*0.1) * (10/5) = 3.0 * 1.5 * 2.0 = 9.0
        assert weight.total_weight == 9.0


class TestAllocationRecord:
    """Test suite for AllocationRecord dataclass."""

    def test_utilization_calculation(self):
        """Test utilization ratio calculation."""
        record = AllocationRecord(
            node_id="M111",
            allocated=1000,
            consumed=500
        )
        assert record.utilization == 0.5

    def test_zero_allocation_utilization(self):
        """Test utilization with zero allocation."""
        record = AllocationRecord(
            node_id="M111",
            allocated=0,
            consumed=0
        )
        assert record.utilization == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
