# Extensibility Guide

## Extending the BST Orchestration System

### 1. Adding New Leaf Nodes

#### 1.1 When to Add Leaves

Add a new leaf when you need to:
- Interface with a new external system
- Split an existing leaf's responsibilities
- Add new I/O capability

#### 1.2 Steps to Add a Leaf Node

1. **Create directory structure**:
```bash
mkdir -p tree/M223/{src,tests,config,coverage}
touch tree/M223/src/__init__.py
```

2. **Implement the node**:
```python
# tree/M223/src/main.py
from shared.types import LeafNode, NodeConfig, NodeLevel, NodeType

class NewInterfaceNode(LeafNode):
    def __init__(self):
        config = NodeConfig(
            node_id="M223",
            name="New Interface",
            level=NodeLevel.LEAF,
            node_type=NodeType.INTERFACE,
            parent_id="M220",  # Parent must be Level 2 node
        )
        super().__init__(config)
        self._interface_type = "new_interface"

    def connect(self) -> bool:
        # Implement connection logic
        return True

    def disconnect(self) -> None:
        # Implement disconnection logic
        pass

    def process(self, input_data: Any) -> NodeResult:
        # Implement processing logic
        pass

def create_node() -> NewInterfaceNode:
    return NewInterfaceNode()
```

3. **Update parent node** to include new child

4. **Add documentation** (PRD.md, PLAN.md, TODO.md)

5. **Write tests**

### 2. Adding New Internal Nodes

#### 2.1 Extending Tree Depth

To add Level 4 (making current leaves Level 3 internal nodes):

```python
# Current M222 becomes internal, new M2221/M2222 are leaves
class PDFCoordinatorNode(InternalNode):  # Was PDFGeneratorNode
    def _init_children(self):
        self.left = create_pdf_writer()   # M2221
        self.right = create_pdf_reader()  # M2222
```

**Note**: This changes tree structure significantly.

### 3. Adding New Workflows

#### 3.1 Define Workflow in Root Node

```python
# In M000/src/main.py

def _execute_custom_workflow(self, data: Dict) -> NodeResult:
    """Execute custom workflow."""
    tokens_used = 50

    # Step 1: Your first step
    step1_result = self.left.process({...})
    tokens_used += step1_result.tokens_used

    # Step 2: Your second step
    step2_result = self.right.process({...})
    tokens_used += step2_result.tokens_used

    return NodeResult(
        success=step1_result.success and step2_result.success,
        data={...},
        tokens_used=tokens_used,
        node_id=self.node_id
    )
```

#### 3.2 Register Workflow

```python
elif action == "full_workflow":
    workflow_type = input_data.get("workflow_type")

    if workflow_type == "custom_workflow":
        return self._execute_custom_workflow(data)
```

### 4. Custom Token Balancing

#### 4.1 Custom Weight Calculator

```python
class CustomTokenBalancer(TokenBalancer):
    def _calculate_weight(self, node: Any) -> float:
        # Custom weight calculation
        base_weight = super()._calculate_weight(node)

        # Add custom factors
        if node.node_id in HIGH_PRIORITY_NODES:
            return base_weight * 2.0

        return base_weight
```

### 5. Adding New External Interfaces

#### 5.1 Define Interface Contract

```python
# shared/interfaces/external.py

class NewInterface(ABC):
    @abstractmethod
    def connect(self) -> InterfaceResult:
        pass

    @abstractmethod
    def operation(self, params: Dict) -> InterfaceResult:
        pass
```

#### 5.2 Implement Mock for Testing

```python
class MockNewInterface(NewInterface):
    def connect(self) -> InterfaceResult:
        return InterfaceResult(success=True)

    def operation(self, params: Dict) -> InterfaceResult:
        # Mock implementation
        return InterfaceResult(success=True, data={...})
```

### 6. Plugin Architecture (Future)

#### 6.1 Proposed Plugin System

```python
class NodePlugin:
    """Base class for node plugins."""

    def pre_process(self, node: BSTNode, data: Any) -> Any:
        """Called before node processing."""
        return data

    def post_process(self, node: BSTNode, result: NodeResult) -> NodeResult:
        """Called after node processing."""
        return result

# Usage
node.register_plugin(LoggingPlugin())
node.register_plugin(MetricsPlugin())
```

### 7. Extensibility Checklist

When extending the system:

- [ ] Follow the Leaf Law (external I/O only in leaves)
- [ ] Maintain binary tree structure
- [ ] Implement factory function (`create_node()`)
- [ ] Add unit tests
- [ ] Update parent node if adding children
- [ ] Document in PRD.md
- [ ] Update token budget allocation
- [ ] Add to scenario tests if applicable

### 8. Migration Guide

#### From Mock to Real Implementation

```python
# 1. Create real interface
class RealDatabaseInterface(DatabaseInterface):
    def connect(self, conn_string: str) -> InterfaceResult:
        import psycopg2
        self._conn = psycopg2.connect(conn_string)
        return InterfaceResult(success=True)

# 2. Update node to use real interface
class SQLDatabaseNode(LeafNode):
    def connect(self) -> bool:
        if os.getenv("USE_MOCK", "true") == "true":
            self._interface = MockDatabaseInterface()
        else:
            self._interface = RealDatabaseInterface()
        return self._interface.connect(os.getenv("DB_URL"))
```
