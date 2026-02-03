#!/usr/bin/env python3
"""
Run coverage.py for all BST nodes and generate reports.

Usage:
    python scripts/run_coverage.py [--node NODE_ID] [--html]
"""
import subprocess
import sys
import os
from pathlib import Path


def run_coverage(node_id: str = None, html: bool = False):
    """Run coverage for specified node or all nodes."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    if node_id:
        # Run coverage for specific node
        test_path = f"tree/{node_id}/tests"
        source_path = f"tree/{node_id}/src"

        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            f"--cov={source_path}",
            "--cov-report=term-missing",
            "-v"
        ]

        if html:
            cmd.append(f"--cov-report=html:tree/{node_id}/coverage/html")

        print(f"\n{'='*60}")
        print(f"Running coverage for node: {node_id}")
        print(f"{'='*60}\n")

    else:
        # Run coverage for all nodes
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=shared",
            "--cov=tree",
            "--cov-report=term-missing",
            "-v"
        ]

        if html:
            cmd.append("--cov-report=html:coverage_html")

        print(f"\n{'='*60}")
        print("Running coverage for ALL nodes")
        print(f"{'='*60}\n")

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def generate_coverage_table():
    """Generate coverage table for README."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run coverage and capture output
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=shared",
        "--cov=tree",
        "--cov-report=term",
        "-q"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("\n## Coverage Table\n")
    print("| Module | Statements | Missing | Coverage |")
    print("|--------|------------|---------|----------|")

    # Parse coverage output (simplified)
    for line in result.stdout.split('\n'):
        if 'tree/' in line or 'shared/' in line:
            parts = line.split()
            if len(parts) >= 4:
                module = parts[0].replace('tree/', '').replace('/src/main', '')
                stmts = parts[1] if len(parts) > 1 else "?"
                miss = parts[2] if len(parts) > 2 else "?"
                cover = parts[3] if len(parts) > 3 else "?"
                print(f"| {module} | {stmts} | {miss} | {cover} |")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run coverage for BST nodes")
    parser.add_argument("--node", "-n", help="Specific node ID (e.g., M111)")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--table", action="store_true", help="Generate coverage table")

    args = parser.parse_args()

    if args.table:
        generate_coverage_table()
    else:
        exit_code = run_coverage(args.node, args.html)
        sys.exit(exit_code)
