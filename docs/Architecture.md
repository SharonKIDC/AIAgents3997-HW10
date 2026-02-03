# Architecture Document

## BST Orchestration System Architecture

### 1. Overview

The system implements a Binary Spanning Tree (BST) architecture for AI agent orchestration, following principles from Dr. Rami Segal's textbook.

### 2. Architectural Principles

#### 2.1 Binary Spanning Tree
- Every node has at most 2 children (left, right)
- Maximum depth of 4 levels (log₂(15) ≈ 4)
- Enables O(log n) traversal operations

#### 2.2 The Leaf Law
**Critical Principle**: External interfaces are ONLY permitted in leaf nodes.

```
Internal Nodes (Levels 0-2):
- Coordinate children
- Aggregate results
- NO external I/O

Leaf Nodes (Level 3):
- Interface with external systems
- File I/O, Database, HTTP, APIs
- Encapsulate external dependencies
```

#### 2.3 Token-Based Resource Management
- Fixed total budget allocated at root
- Weighted distribution to leaves
- Consumption tracking per node

### 3. System Structure

```
                         [M000]
                    Root Orchestrator
                   /                \
           [M100]                    [M200]
      Infrastructure              Application
        /        \                  /        \
    [M110]      [M120]          [M210]      [M220]
   Config      Database         Server      Output
   /    \       /    \          /    \       /    \
[M111][M112][M121][M122]    [M211][M212][M221][M222]
```

### 4. Layer Definitions

#### Layer 0: Root (M000)
- **Responsibility**: System-wide orchestration
- **Components**: TokenBalancer, Workflow Engine
- **Children**: M100, M200

#### Layer 1: Managers (M100, M200)
- **M100 (Infrastructure)**: Config, logging, data persistence
- **M200 (Application)**: MCP server, outputs

#### Layer 2: Handlers (M110, M120, M210, M220)
- Coordinate pairs of leaf nodes
- Aggregate child results
- Route requests to appropriate leaf

#### Layer 3: Interfaces (M111-M222)
- **Only layer with external I/O**
- Each leaf handles one external system type
- Mock interfaces for testing

### 5. Data Flow Patterns

#### 5.1 Top-Down (Command)
```
M000 → M100 → M110 → M111
       ↓
Request flows down tree to appropriate leaf
```

#### 5.2 Bottom-Up (Response)
```
M111 → M110 → M100 → M000
                      ↑
Results aggregate up through parent nodes
```

#### 5.3 Cross-Tree (Workflow)
```
M000 → M100 → M120 → M122 (query)
  ↓
M000 → M200 → M220 → M222 (output)
```

### 6. Component Interfaces

#### 6.1 Node Base Classes

```python
class BSTNode(ABC):
    """Abstract base for all nodes."""
    config: NodeConfig
    left: Optional[BSTNode]
    right: Optional[BSTNode]

    @abstractmethod
    def process(self, input_data: Any) -> NodeResult

class LeafNode(BSTNode):
    """Base for leaf nodes with external interfaces."""
    @abstractmethod
    def connect(self) -> bool
    @abstractmethod
    def disconnect(self) -> None

class InternalNode(BSTNode):
    """Base for internal nodes."""
    def aggregate_results(self, left: NodeResult, right: NodeResult) -> NodeResult
```

#### 6.2 Communication Protocol

```python
@dataclass
class NodeResult:
    success: bool
    data: Any
    error: Optional[str]
    tokens_used: int
    node_id: str
```

### 7. Token Distribution Algorithm

```python
def distribute(node, budget):
    if node.is_leaf:
        allocate(node, budget)
        return

    left_weight = calculate_weight(node.left)
    right_weight = calculate_weight(node.right)
    total = left_weight + right_weight

    distribute(node.left, budget * left_weight / total)
    distribute(node.right, budget * right_weight / total)
```

**Complexity**:
- Distribution: O(n)
- Query: O(1)
- Rebalance: O(n²)

### 8. Error Handling Strategy

1. **Leaf Level**: Catch external errors, return NodeResult with error
2. **Internal Levels**: Aggregate errors from children
3. **Root Level**: Log errors, decide on retry or fail

### 9. Testing Architecture

```
Unit Tests (per node)
    ↓
Integration Tests (parent-child pairs)
    ↓
System Tests (full tree workflows)
    ↓
Scenario Tests (10 documented scenarios)
```

### 10. Deployment Considerations

Current implementation uses mock interfaces. For production:
- Replace mock interfaces with real implementations
- Add connection pooling for database
- Implement retry logic for external APIs
- Add monitoring and alerting

### 11. Security Boundaries

External access points (leaf nodes only):
- M111: File system (YAML)
- M112: File system (logs)
- M121: File system (Excel)
- M122: Database
- M211: External LLM API
- M212: External resource API
- M221: HTTP endpoints
- M222: File system (PDF)

All other nodes have NO external access.
