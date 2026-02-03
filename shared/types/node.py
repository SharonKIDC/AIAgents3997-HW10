"""
BST Node Type Definitions
Binary Spanning Tree Architecture for Agent Orchestration
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable


class NodeLevel(Enum):
    """BST tree level enumeration."""
    ROOT = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEAF = 3


class NodeType(Enum):
    """Node type classification."""
    ORCHESTRATOR = "orchestrator"  # Root node
    MANAGER = "manager"            # Level 1 nodes
    HANDLER = "handler"            # Level 2 nodes
    INTERFACE = "interface"        # Leaf nodes


@dataclass
class NodeConfig:
    """Configuration for a BST node."""
    node_id: str
    name: str
    level: NodeLevel
    node_type: NodeType
    parent_id: Optional[str] = None
    left_child_id: Optional[str] = None
    right_child_id: Optional[str] = None
    token_budget: int = 1000
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeResult:
    """Result of a node operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    tokens_used: int = 0
    node_id: str = ""


class BSTNode(ABC):
    """Abstract base class for all BST nodes."""

    def __init__(self, config: NodeConfig):
        self.config = config
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None
        self.parent: Optional['BSTNode'] = None
        self._token_allocation: int = config.token_budget
        self._tokens_consumed: int = 0

    @property
    def node_id(self) -> str:
        return self.config.node_id

    @property
    def is_leaf(self) -> bool:
        return self.config.level == NodeLevel.LEAF

    @property
    def tokens_remaining(self) -> int:
        return self._token_allocation - self._tokens_consumed

    def consume_tokens(self, amount: int) -> bool:
        """Consume tokens from allocation. Returns False if insufficient."""
        if amount > self.tokens_remaining:
            return False
        self._tokens_consumed += amount
        return True

    def reset_tokens(self) -> None:
        """Reset token consumption."""
        self._tokens_consumed = 0

    def set_allocation(self, tokens: int) -> None:
        """Set token allocation from parent."""
        self._token_allocation = tokens

    @abstractmethod
    def process(self, input_data: Any) -> NodeResult:
        """Process input and return result. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return node status information."""
        pass


class LeafNode(BSTNode):
    """Base class for leaf nodes with external interfaces."""

    def __init__(self, config: NodeConfig):
        if config.level != NodeLevel.LEAF:
            raise ValueError("LeafNode must have LEAF level")
        super().__init__(config)
        self._interface_type: str = ""
        self._mock_mode: bool = True

    @property
    def interface_type(self) -> str:
        return self._interface_type

    @abstractmethod
    def connect(self) -> bool:
        """Connect to external interface."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from external interface."""
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "level": self.config.level.name,
            "interface_type": self._interface_type,
            "mock_mode": self._mock_mode,
            "tokens_remaining": self.tokens_remaining,
        }


class InternalNode(BSTNode):
    """Base class for internal (non-leaf) nodes."""

    def __init__(self, config: NodeConfig):
        if config.level == NodeLevel.LEAF:
            raise ValueError("InternalNode cannot have LEAF level")
        super().__init__(config)

    def aggregate_results(self, left_result: NodeResult, right_result: NodeResult) -> NodeResult:
        """Aggregate results from child nodes."""
        combined_tokens = left_result.tokens_used + right_result.tokens_used

        if not left_result.success and not right_result.success:
            return NodeResult(
                success=False,
                error=f"Both children failed: {left_result.error}, {right_result.error}",
                tokens_used=combined_tokens,
                node_id=self.node_id
            )

        return NodeResult(
            success=True,
            data={"left": left_result.data, "right": right_result.data},
            tokens_used=combined_tokens,
            node_id=self.node_id
        )

    def get_status(self) -> Dict[str, Any]:
        left_status = self.left.get_status() if self.left else None
        right_status = self.right.get_status() if self.right else None

        return {
            "node_id": self.node_id,
            "level": self.config.level.name,
            "tokens_remaining": self.tokens_remaining,
            "left_child": left_status,
            "right_child": right_status,
        }
