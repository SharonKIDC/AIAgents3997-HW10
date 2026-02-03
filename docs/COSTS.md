# Cost Analysis

## BST Orchestration Resource Costs

### 1. Token Cost Model

#### 1.1 Base Costs per Operation

| Operation Type | Base Tokens | Variable Cost |
|---------------|-------------|---------------|
| Node initialization | 5 | - |
| Config read | 10 | +bytes/100 |
| Config write | 10 | +bytes/50 |
| Log write | 5 | +message_len/100 |
| Excel read | 15 | +rows*5 |
| Excel write | 15 | +rows*10 |
| DB query | 20 | +results*5 |
| DB insert | 30 | - |
| API call | 50 | +response_size/10 |
| PDF generate | 40 | +pages*20 |
| HTTP request | 25 | +body_size/15 |

#### 1.2 Node-Specific Costs

| Node | Typical Operation | Est. Tokens |
|------|-------------------|-------------|
| M111 | Read config | 15-30 |
| M112 | Write log entry | 5-15 |
| M121 | Read tenant sheet | 30-100 |
| M122 | Query tenants | 35-80 |
| M211 | Call MCP tool | 80-150 |
| M212 | Fetch resource | 40-80 |
| M221 | API GET request | 30-60 |
| M222 | Generate PDF | 60-120 |

### 2. Workflow Costs

#### 2.1 Scenario Token Consumption

| Scenario | Measured Tokens | Nodes Used |
|----------|-----------------|------------|
| 1. Config Load | ~100-120 | 4 |
| 2. Tenant Query | ~90-100 | 4 |
| 3. Excel Import | ~85-95 | 4 |
| 4. MCP Tool Call | ~130-140 | 4 |
| 5. PDF Generation | ~160-170 | 4 |
| 6. Web API Request | ~90-100 | 4 |
| 7. Hierarchical Merge | ~145-150 | 3 |
| 8. Error Propagation | ~75-85 | 3 |
| 9. Load Rebalancing | ~25-35 | 15 |
| 10. Full Pipeline | ~400-450 | 8+ |

#### 2.2 Typical Workflow Costs

```
tenant_report workflow:
├── Config load (M111): ~20 tokens
├── DB query (M122): ~40 tokens
├── MCP process (M211): ~80 tokens
├── PDF generate (M222): ~60 tokens
└── Overhead (internal nodes): ~50 tokens
Total: ~250 tokens
```

### 3. Budget Planning

#### 3.1 Budget Allocation Strategy

**Conservative** (high safety margin):
```
Total: 100,000 tokens
├── M100 subtree: 50,000 (50%)
│   ├── Config (M110): 25,000
│   └── Database (M120): 25,000
└── M200 subtree: 50,000 (50%)
    ├── Server (M210): 25,000
    └── Output (M220): 25,000
```

**Optimized** (based on usage patterns):
```
Total: 100,000 tokens
├── M100 subtree: 35,000 (35%)
│   ├── Config (M110): 10,000
│   └── Database (M120): 25,000
└── M200 subtree: 65,000 (65%)
    ├── Server (M210): 35,000
    └── Output (M220): 30,000
```

### 4. Cost Optimization

#### 4.1 Techniques

1. **Caching**: Cache config reads (M111)
2. **Batching**: Batch database queries (M122)
3. **Compression**: Compress large responses
4. **Early termination**: Stop workflows on failure

#### 4.2 Weight Tuning

```python
# Increase allocation for high-usage nodes
balancer.update_weight("M211",
    historical_usage=2.0,  # Double historical weight
    priority=8             # Higher priority
)

# Decrease allocation for low-usage nodes
balancer.update_weight("M112",
    historical_usage=0.5,
    priority=3
)
```

### 5. Monitoring Costs

#### 5.1 Per-Run Metrics

```python
# Get utilization report after workflow
report = root._token_balancer.get_utilization_report()

for node_id, info in report.items():
    if info["utilization"] > "80%":
        print(f"WARNING: {node_id} high utilization")
```

#### 5.2 Alerts

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Leaf utilization | >80% | Rebalance |
| Total consumption | >90% | Pause workflows |
| Single operation | >1000 tokens | Log warning |

### 6. Projected Costs at Scale

#### Operations per Day Estimate

| Volume | Workflows/Day | Tokens/Day | Rebalances |
|--------|---------------|------------|------------|
| Low | 100 | ~30,000 | 1 |
| Medium | 1,000 | ~300,000 | 3-5 |
| High | 10,000 | ~3,000,000 | 10-20 |

### 7. Cost Summary

**Current Implementation**:
- Total budget: 100,000 tokens
- Average workflow: ~200 tokens
- Max workflows per budget: ~500

**Recommendations**:
1. Monitor leaf utilization
2. Rebalance when any leaf exceeds 70%
3. Consider budget increase for high-volume scenarios
