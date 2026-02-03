"""
Token Balancer - Load Control Algorithm for BST Agent Orchestration

Implements token budget distribution across BST leaves based on:
- Historical usage patterns
- Current queue depth
- Processing complexity estimates

Complexity Analysis (O Notation):
- Token query: O(1) - hash lookup
- Single leaf balance: O(log n) - tree depth traversal
- Partial rebalance: O(n) - subtree update
- Full rebalance: O(n²) - all paths + weight recalc
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random


@dataclass
class NodeWeight:
    """Weight factors for a node."""
    historical_usage: float = 1.0
    queue_depth: int = 0
    complexity: float = 1.0
    priority: int = 5  # 1-10 scale

    @property
    def total_weight(self) -> float:
        """Calculate total weight factor."""
        base = self.historical_usage * self.complexity
        queue_factor = 1 + (self.queue_depth * 0.1)
        priority_factor = self.priority / 5.0
        return base * queue_factor * priority_factor


@dataclass
class AllocationRecord:
    """Record of token allocation."""
    node_id: str
    allocated: int
    consumed: int = 0
    timestamp: float = 0.0

    @property
    def utilization(self) -> float:
        """Return utilization ratio."""
        if self.allocated == 0:
            return 0.0
        return self.consumed / self.allocated


class TokenBalancer:
    """
    Distributes token budget across BST leaves.
    Based on Chapter 4 principles from the textbook.
    """

    def __init__(self, total_budget: int = 100000):
        self.total_budget = total_budget
        self.leaf_allocations: Dict[str, AllocationRecord] = {}
        self.node_weights: Dict[str, NodeWeight] = {}
        self._weight_cache: Dict[str, float] = {}
        self._cache_valid: bool = False

    def get_allocation(self, node_id: str) -> int:
        """
        Get current token allocation for a node.

        Time Complexity: O(1)
        - Direct dictionary lookup via hash table
        - Constant time regardless of tree size
        """
        if node_id in self.leaf_allocations:
            return self.leaf_allocations[node_id].allocated
        return 0

    def balance_tokens(self, tree_root: Any) -> Dict[str, int]:
        """
        Distribute tokens across all leaves starting from root.

        Time Complexity Analysis:
        - Best Case: O(1) - cached allocation lookup
        - Average Case: O(log n) - tree traversal to leaf
        - Worst Case: O(n) - full tree traversal when cache invalid
        """
        self._invalidate_cache()
        self._distribute(tree_root, self.total_budget)
        return {k: v.allocated for k, v in self.leaf_allocations.items()}

    def _distribute(self, node: Any, available_budget: int) -> int:
        """
        Recursive distribution algorithm.

        Time Complexity: O(log n) per leaf path
        - Binary tree traversal from root to leaf
        - Depth is log₂(n) for balanced tree
        """
        if node is None:
            return 0

        if node.is_leaf:
            # O(1) - direct assignment
            self.leaf_allocations[node.node_id] = AllocationRecord(
                node_id=node.node_id,
                allocated=available_budget
            )
            node.set_allocation(available_budget)
            return available_budget

        # O(log n) - binary split down tree
        left_weight = self._calculate_weight(node.left)
        right_weight = self._calculate_weight(node.right)
        total_weight = left_weight + right_weight

        if total_weight == 0:
            total_weight = 1  # Prevent division by zero

        left_budget = int(available_budget * (left_weight / total_weight))
        right_budget = available_budget - left_budget

        self._distribute(node.left, left_budget)
        self._distribute(node.right, right_budget)

        return available_budget

    def _calculate_weight(self, node: Any) -> float:
        """
        Calculate weight for a node subtree.

        Time Complexity:
        - O(1) with memoization (cache hit)
        - O(n) without memoization (full subtree traversal)
        """
        if node is None:
            return 0.0

        # Check cache first - O(1)
        if self._cache_valid and node.node_id in self._weight_cache:
            return self._weight_cache[node.node_id]

        # Calculate weight
        if node.is_leaf:
            weight = self._get_node_weight(node.node_id).total_weight
        else:
            # Sum of children weights
            left_w = self._calculate_weight(node.left)
            right_w = self._calculate_weight(node.right)
            weight = left_w + right_w

        # Cache result - O(1)
        self._weight_cache[node.node_id] = weight
        return weight

    def _get_node_weight(self, node_id: str) -> NodeWeight:
        """Get or create weight for node."""
        if node_id not in self.node_weights:
            self.node_weights[node_id] = NodeWeight()
        return self.node_weights[node_id]

    def update_weight(self, node_id: str, **kwargs) -> None:
        """
        Update weight factors for a node.

        Time Complexity: O(1)
        - Dictionary update operations
        """
        weight = self._get_node_weight(node_id)
        for key, value in kwargs.items():
            if hasattr(weight, key):
                setattr(weight, key, value)
        self._invalidate_cache()

    def record_consumption(self, node_id: str, tokens_used: int) -> None:
        """
        Record token consumption for a node.

        Time Complexity: O(1)
        """
        if node_id in self.leaf_allocations:
            self.leaf_allocations[node_id].consumed += tokens_used

    def rebalance_partial(self, subtree_root: Any) -> Dict[str, int]:
        """
        Rebalance only a subtree.

        Time Complexity: O(n) where n is subtree size
        - Visits all nodes in subtree
        - Proportional to subtree size
        """
        if subtree_root is None:
            return {}

        # Calculate current budget for subtree
        subtree_budget = self._get_subtree_budget(subtree_root)

        # Clear allocations for subtree nodes
        self._clear_subtree_allocations(subtree_root)

        # Redistribute
        self._distribute(subtree_root, subtree_budget)

        return {k: v.allocated for k, v in self.leaf_allocations.items()}

    def rebalance_full(self, tree_root: Any) -> Dict[str, int]:
        """
        Complete rebalancing when weights change significantly.

        Time Complexity: O(n²)
        - Recalculates all dependencies
        - For each node O(n), recalculate weights involving all nodes O(n)
        """
        # Clear all caches and allocations
        self._invalidate_cache()
        self.leaf_allocations.clear()

        # Recalculate all weights from scratch - O(n)
        self._recalculate_all_weights(tree_root)

        # Redistribute tokens - O(n)
        self._distribute(tree_root, self.total_budget)

        return {k: v.allocated for k, v in self.leaf_allocations.items()}

    def _recalculate_all_weights(self, node: Any) -> None:
        """
        Recalculate all node weights.

        Time Complexity: O(n) for traversal, O(n) per weight calc = O(n²) total
        """
        if node is None:
            return

        # Update historical usage based on consumption
        if node.node_id in self.leaf_allocations:
            record = self.leaf_allocations[node.node_id]
            weight = self._get_node_weight(node.node_id)
            if record.utilization > 0.8:
                weight.historical_usage *= 1.1  # Increase weight
            elif record.utilization < 0.2:
                weight.historical_usage *= 0.9  # Decrease weight

        # Recurse to children
        if hasattr(node, 'left') and node.left:
            self._recalculate_all_weights(node.left)
        if hasattr(node, 'right') and node.right:
            self._recalculate_all_weights(node.right)

    def _get_subtree_budget(self, node: Any) -> int:
        """Calculate total budget allocated to a subtree."""
        if node is None:
            return 0
        if node.is_leaf:
            return self.get_allocation(node.node_id)
        return (self._get_subtree_budget(node.left) +
                self._get_subtree_budget(node.right))

    def _clear_subtree_allocations(self, node: Any) -> None:
        """Clear allocations for all nodes in subtree."""
        if node is None:
            return
        if node.is_leaf and node.node_id in self.leaf_allocations:
            del self.leaf_allocations[node.node_id]
        if hasattr(node, 'left'):
            self._clear_subtree_allocations(node.left)
        if hasattr(node, 'right'):
            self._clear_subtree_allocations(node.right)

    def _invalidate_cache(self) -> None:
        """Invalidate weight cache."""
        self._cache_valid = False
        self._weight_cache.clear()

    def get_utilization_report(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate utilization report for all leaves.

        Time Complexity: O(n) - iterate over all allocations
        """
        report = {}
        for node_id, record in self.leaf_allocations.items():
            report[node_id] = {
                "allocated": record.allocated,
                "consumed": record.consumed,
                "utilization": f"{record.utilization:.1%}",
                "remaining": record.allocated - record.consumed,
            }
        return report

    def simulate_load(self, node_id: str) -> int:
        """
        Simulate random load for a node (for testing).
        Returns simulated token consumption.
        """
        allocation = self.get_allocation(node_id)
        if allocation == 0:
            return 0

        # Random consumption between 10% and 90% of allocation
        consumption = random.randint(
            int(allocation * 0.1),
            int(allocation * 0.9)
        )
        self.record_consumption(node_id, consumption)
        return consumption
