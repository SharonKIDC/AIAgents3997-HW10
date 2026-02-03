# Security Documentation

## BST Orchestration Security Considerations

### 1. Security Architecture

#### 1.1 The Leaf Law as Security Boundary

The Leaf Law provides inherent security benefits:
- **Attack Surface Reduction**: External interfaces limited to 8 leaf nodes
- **Clear Boundaries**: Easy to identify and audit external access points
- **Isolation**: Internal nodes have no direct external access

```
EXTERNAL WORLD
      │
      ▼
┌─────────────────────────────────────────┐
│ LEAF NODES (Security Boundary)          │
│ M111, M112, M121, M122, M211-M222       │
└─────────────────────────────────────────┘
      │ (Internal only below this line)
      ▼
┌─────────────────────────────────────────┐
│ INTERNAL NODES                          │
│ M110, M120, M210, M220, M100, M200, M000│
└─────────────────────────────────────────┘
```

### 2. External Interface Security

#### 2.1 File System (M111, M112, M121, M222)

**Risks**:
- Path traversal attacks
- Unauthorized file access
- File injection

**Mitigations**:
- Validate file paths against allowed directories
- Use allowlists for file extensions
- Sanitize user-provided paths

```python
ALLOWED_PATHS = ["config/", "data/", "logs/", "reports/"]
ALLOWED_EXTENSIONS = [".yaml", ".yml", ".xlsx", ".pdf", ".log"]
```

#### 2.2 Database (M122)

**Risks**:
- SQL injection
- Data exposure
- Connection string leakage

**Mitigations**:
- Use parameterized queries (implemented)
- Validate input parameters
- Store connection strings in environment variables

```python
# Safe: Parameterized query
interface.query("SELECT * FROM tenants WHERE id = :id", {"id": tenant_id})

# Unsafe: String concatenation (NOT used)
# interface.query(f"SELECT * FROM tenants WHERE id = {tenant_id}")
```

#### 2.3 HTTP (M221)

**Risks**:
- Request forgery
- Response injection
- Authentication bypass

**Mitigations**:
- Validate URLs against allowlist
- Sanitize response data
- Implement request signing for production

#### 2.4 External API (M211, M212)

**Risks**:
- API key exposure
- Prompt injection
- Response manipulation

**Mitigations**:
- Store API keys in environment variables
- Validate/sanitize LLM responses
- Rate limiting

### 3. Token Security

Token budget prevents resource exhaustion:

```python
def consume_tokens(self, amount: int) -> bool:
    if amount > self.tokens_remaining:
        return False  # Prevent over-consumption
    self._tokens_consumed += amount
    return True
```

### 4. Configuration Security

#### 4.1 Secrets Management

**DO NOT** store secrets in:
- Source code
- config.json files
- Git repository

**DO** store secrets in:
- Environment variables
- `.env` files (gitignored)
- Secret management systems

#### 4.2 Example .env Structure

```bash
# .env (NOT committed to git)
BST_DB_PASSWORD=secure_password_here
BST_API_KEY=api_key_here
```

### 5. Input Validation

All external inputs validated at leaf nodes:

```python
def validate_input(self, data: Dict) -> bool:
    """Validate input before processing."""
    if "action" not in data:
        return False
    if data["action"] not in ALLOWED_ACTIONS:
        return False
    return True
```

### 6. Error Handling

Errors sanitized before returning:

```python
except Exception as e:
    # Log full error internally
    logger.error(f"Full error: {e}")

    # Return sanitized error to caller
    return NodeResult(
        success=False,
        error="Operation failed",  # Generic message
        node_id=self.node_id
    )
```

### 7. Audit Points

| Node | Audit Item | Frequency |
|------|------------|-----------|
| M111 | Config file access | Per access |
| M112 | Log file writes | Daily |
| M122 | Database queries | Per query |
| M221 | HTTP requests | Per request |
| M211 | LLM API calls | Per call |
| M000 | Token consumption | Per workflow |

### 8. Security Checklist

- [ ] No secrets in source code
- [ ] Environment variables for sensitive config
- [ ] Input validation at leaf nodes
- [ ] Parameterized database queries
- [ ] Path validation for file operations
- [ ] Error messages sanitized
- [ ] Token limits enforced
- [ ] Logging of security events

### 9. Known Limitations (Mock Implementation)

Current implementation uses mocks. For production:

1. **Add authentication** to HTTP endpoints
2. **Implement TLS** for all external connections
3. **Add API key rotation** for external services
4. **Implement audit logging** with tamper protection
5. **Add rate limiting** at leaf nodes
