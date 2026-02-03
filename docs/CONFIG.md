# Configuration Guide

## BST Orchestration Configuration

### 1. Project Configuration

#### pyproject.toml
Main project configuration file containing:
- Build system settings
- Project metadata
- pytest configuration
- coverage settings
- linter settings

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["shared/tests", "tree"]

[tool.coverage.run]
source = ["shared", "tree"]
branch = true
```

### 2. Node Configuration

Each node has a `config/config.json` file:

```json
{
  "node_id": "M000",
  "name": "Root Orchestrator",
  "level": 0,
  "type": "orchestrator",
  "token_budget": 100000,
  "children": {
    "left": "M100",
    "right": "M200"
  }
}
```

#### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Unique node identifier (M000-M222) |
| `name` | string | Human-readable node name |
| `level` | int | Tree level (0-3) |
| `type` | string | orchestrator/manager/handler/interface |
| `token_budget` | int | Default token allocation |
| `parent` | string | Parent node ID (null for root) |
| `children` | object | Left and right child IDs |
| `external_interface` | string | Interface type (leaf nodes only) |

### 3. Token Budget Configuration

Default budget allocation:

```
Total Budget: 100,000 tokens

Distribution:
├── M100 (50,000)
│   ├── M110 (25,000)
│   │   ├── M111: 12,500
│   │   └── M112: 12,500
│   └── M120 (25,000)
│       ├── M121: 12,500
│       └── M122: 12,500
└── M200 (50,000)
    ├── M210 (25,000)
    │   ├── M211: 12,500
    │   └── M212: 12,500
    └── M220 (25,000)
        ├── M221: 12,500
        └── M222: 12,500
```

### 4. Environment Variables

See `.env.example` for available environment variables:

```bash
# Token Configuration
BST_TOTAL_BUDGET=100000

# Logging
BST_LOG_LEVEL=INFO
BST_LOG_PATH=logs/

# Database (M122)
BST_DB_PATH=data/tenant.db

# API Configuration (M211, M212)
BST_API_TIMEOUT=30
BST_API_RETRY_COUNT=3
```

### 5. Leaf Node Interface Configuration

#### M111 - YAML Config
```json
{
  "external_interface": {
    "type": "file",
    "formats": [".yaml", ".yml"],
    "default_path": "config/settings.yaml"
  }
}
```

#### M122 - SQL Database
```json
{
  "external_interface": {
    "type": "database",
    "db_types": ["sqlite", "postgresql"],
    "connection_string": "sqlite:///tenant.db"
  }
}
```

#### M221 - Web Interface
```json
{
  "external_interface": {
    "type": "http",
    "protocol": "REST",
    "base_url": "http://localhost:8000"
  }
}
```

### 6. Runtime Configuration

```python
from tree.M000.src.main import build_tree

# Build tree with custom budget
root = build_tree(total_budget=50000)

# Configure weights for specific nodes
root._token_balancer.update_weight(
    "M111",
    historical_usage=2.0,
    priority=10
)
```

### 7. Testing Configuration

```bash
# Run with specific coverage target
pytest --cov=tree --cov-fail-under=80

# Run specific node tests
pytest tree/M111/tests/ -v

# Generate HTML coverage report
pytest --cov=tree --cov-report=html
```
