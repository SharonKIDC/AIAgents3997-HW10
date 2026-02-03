# Quality Standards

## BST Orchestration Quality Requirements

### 1. Code Quality Standards

#### 1.1 Linting Requirements

**Tool**: flake8
**Configuration**:
```
max-line-length = 120
ignore = E501, W503, E402
```

**Target**: 0 errors

#### 1.2 Type Hints

All public functions must have type hints:

```python
# Good
def process(self, input_data: Any) -> NodeResult:
    pass

# Bad
def process(self, input_data):
    pass
```

#### 1.3 Docstrings

All classes and public methods must have docstrings:

```python
class ExampleNode(LeafNode):
    """
    Brief description of the node.

    Responsibility: What this node does
    External Interface: Type of external I/O (if leaf)
    """

    def process(self, input_data: Any) -> NodeResult:
        """
        Process input and return result.

        Args:
            input_data: Input data dictionary with action and params

        Returns:
            NodeResult with success status, data, and token usage
        """
        pass
```

### 2. Testing Standards

#### 2.1 Coverage Requirements

| Component | Minimum Coverage |
|-----------|------------------|
| shared/types | 80% |
| shared/utils | 80% |
| Leaf nodes | 80% |
| Internal nodes | 75% |
| Root node | 80% |
| **Overall** | **80%** |

#### 2.2 Test Structure

```
tree/Mxxx/tests/
└── test_mxxx.py
    ├── TestMockInterface
    │   ├── test_operation_1
    │   └── test_operation_2
    └── TestNode
        ├── test_creation
        ├── test_connect_disconnect
        ├── test_process_actions
        └── test_token_tracking
```

#### 2.3 Test Naming

```python
# Pattern: test_<what>_<expected_behavior>
def test_process_read_action_returns_config(self):
    pass

def test_process_unknown_action_returns_error(self):
    pass
```

### 3. Documentation Standards

#### 3.1 Required Files per Node

| File | Purpose | Required |
|------|---------|----------|
| PRD.md | Requirements | Yes |
| PLAN.md | Implementation plan | Yes |
| TODO.md | Task tracking | Yes |
| README.md | Quick reference | Yes |
| config/config.json | Configuration | Yes |

#### 3.2 PRD Template

```markdown
# Mxxx - Node Name PRD

## Overview
Brief description

## Node Information
- **Node ID**: Mxxx
- **Level**: 0-3
- **Type**: orchestrator/manager/handler/interface
- **Parent**: Myyy or None
- **Children**: Maaa, Mbbb or None

## External Interfaces
Description of external I/O (leaf only)

## Token Budget
Default allocation
```

### 4. Architecture Standards

#### 4.1 The Leaf Law

**MANDATORY**: External interfaces ONLY in leaf nodes (Level 3)

```
✓ M111 reads YAML files (leaf)
✓ M122 queries database (leaf)
✗ M110 reads files directly (internal - VIOLATION)
```

#### 4.2 Binary Tree Structure

Every internal node must have exactly 2 children:

```python
# Good
self.left = create_child_a()
self.right = create_child_b()

# Bad - violates binary structure
self.children = [a, b, c]
```

#### 4.3 Node Independence

Each node must be:
- Independently instantiable
- Independently testable
- Self-documenting

### 5. Performance Standards

#### 5.1 Complexity Requirements

| Operation | Maximum Complexity |
|-----------|-------------------|
| Token query | O(1) |
| Node process | O(1) per node |
| Tree traversal | O(log n) |
| Full rebalance | O(n²) |

#### 5.2 Token Efficiency

- Base operation: <50 tokens
- Complex workflow: <500 tokens
- Full pipeline: <1000 tokens

### 6. Security Standards

See [SECURITY.md](../SECURITY.md) for full requirements.

Key points:
- No secrets in code
- Input validation at leaves
- Parameterized queries
- Sanitized error messages

### 7. Git Standards

#### 7.1 Commit Messages

```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: feat, fix, docs, test, refactor, chore

#### 7.2 Branch Naming

- `main` - Integration branch
- `node/Mxxx` - Node-specific development
- `feature/description` - Feature branches
- `fix/description` - Bug fixes

### 8. Quality Checklist

Before merging:

- [ ] Linting passes (0 errors)
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] PRD.md updated
- [ ] No secrets in code
- [ ] Leaf Law respected
- [ ] Token tracking implemented
