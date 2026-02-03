#!/usr/bin/env python3
"""
Interactive BST Orchestration Demo

Run: python scripts/demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tree.M000.src.main import build_tree


def main():
    print("=" * 60)
    print("BST Orchestration Demo")
    print("=" * 60)

    # Build tree
    print("\n1. Building BST tree (100k tokens)...")
    root = build_tree(total_budget=100000)
    print(f"   Root: {root.node_id}")
    print(f"   Left child: {root.left.node_id} (Infrastructure)")
    print(f"   Right child: {root.right.node_id} (Application)")

    # Initialize
    print("\n2. Initializing system...")
    root.initialize_system()
    print("   System initialized!")

    # Show tree structure
    print("\n3. Tree Structure:")
    leaves = root._collect_all_leaves()
    print(f"   Total leaves: {len(leaves)}")
    print(f"   Leaf IDs: {[l.node_id for l in leaves]}")

    # Token distribution
    print("\n4. Token Distribution:")
    allocations = root._token_balancer.get_utilization_report()
    for node_id, info in allocations.items():
        print(f"   {node_id}: {info['allocated']} tokens")

    # Run a workflow
    print("\n5. Running 'tenant_report' workflow...")
    result = root.run_workflow("tenant_report", {"id": 1, "name": "Demo Tenant"})
    print(f"   Workflow ID: {result.get('workflow_id')}")
    print(f"   Steps completed: {result.get('steps_completed')}")

    # Full pipeline
    print("\n6. Running 'full_pipeline' workflow...")
    result = root.run_workflow("full_pipeline", {"tenant_id": 1})
    print(f"   Pipeline steps: {result.get('pipeline_steps')}")

    # System status
    print("\n7. Final System Status:")
    status = root.get_system_status()
    print(f"   Uptime: {status.get('system_uptime')}")
    print(f"   Workflows executed: {status.get('workflow_count')}")
    print(f"   Tree nodes: {status['tree_structure']['total_nodes']}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
