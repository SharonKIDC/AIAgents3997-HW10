#!/usr/bin/env python3
"""
Run linter (flake8/pylint) for all BST nodes.

Usage:
    python scripts/run_linter.py [--node NODE_ID] [--tool flake8|pylint]
"""
import subprocess
import sys
import os
from pathlib import Path


def run_flake8(path: str):
    """Run flake8 on specified path."""
    cmd = [
        sys.executable, "-m", "flake8",
        path,
        "--max-line-length=120",
        "--ignore=E501,W503,E402"
    ]
    return subprocess.run(cmd, capture_output=False).returncode


def run_pylint(path: str):
    """Run pylint on specified path."""
    cmd = [
        sys.executable, "-m", "pylint",
        path,
        "--disable=C0114,C0115,C0116,R0903,E0401,W0612",
        "--max-line-length=120"
    ]
    return subprocess.run(cmd, capture_output=False).returncode


def run_linter(node_id: str = None, tool: str = "flake8"):
    """Run linter for specified node or all nodes."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    if node_id:
        paths = [f"tree/{node_id}/src"]
    else:
        paths = ["shared", "tree"]

    print(f"\n{'='*60}")
    print(f"Running {tool} linter")
    print(f"{'='*60}\n")

    total_errors = 0

    for path in paths:
        print(f"\nChecking: {path}")
        print("-" * 40)

        if tool == "flake8":
            result = run_flake8(path)
        else:
            result = run_pylint(path)

        total_errors += result

    if total_errors == 0:
        print("\n✓ All checks passed!")
    else:
        print(f"\n✗ Found issues in {total_errors} check(s)")

    return total_errors


def generate_linter_report():
    """Generate linter report for all nodes."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    nodes = [
        "M000", "M100", "M200",
        "M110", "M120", "M210", "M220",
        "M111", "M112", "M121", "M122", "M211", "M212", "M221", "M222"
    ]

    print("\n## Linter Report\n")
    print("| Node | Status | Issues |")
    print("|------|--------|--------|")

    for node in nodes:
        path = f"tree/{node}/src/main.py"
        if Path(path).exists():
            cmd = [
                sys.executable, "-m", "flake8",
                path,
                "--max-line-length=120",
                "--ignore=E501,W503,E402",
                "--count",
                "-q"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            count = result.stdout.strip() or "0"
            status = "✓" if count == "0" else "✗"
            print(f"| {node} | {status} | {count} |")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run linter for BST nodes")
    parser.add_argument("--node", "-n", help="Specific node ID (e.g., M111)")
    parser.add_argument("--tool", "-t", choices=["flake8", "pylint"],
                        default="flake8", help="Linter tool to use")
    parser.add_argument("--report", action="store_true", help="Generate report table")

    args = parser.parse_args()

    if args.report:
        generate_linter_report()
    else:
        exit_code = run_linter(args.node, args.tool)
        sys.exit(exit_code)
