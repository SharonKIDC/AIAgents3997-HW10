#!/usr/bin/env python3
"""Generate documentation for all BST nodes."""
import json
from pathlib import Path

# Node definitions
NODES = {
    "M000": {"name": "Root Orchestrator", "level": 0, "type": "orchestrator", "parent": None, "left": "M100", "right": "M200", "external": None},
    "M100": {"name": "Infrastructure Manager", "level": 1, "type": "manager", "parent": "M000", "left": "M110", "right": "M120", "external": None},
    "M200": {"name": "Application Manager", "level": 1, "type": "manager", "parent": "M000", "left": "M210", "right": "M220", "external": None},
    "M110": {"name": "Config Handler", "level": 2, "type": "handler", "parent": "M100", "left": "M111", "right": "M112", "external": None},
    "M120": {"name": "Database Handler", "level": 2, "type": "handler", "parent": "M100", "left": "M121", "right": "M122", "external": None},
    "M210": {"name": "Server Handler", "level": 2, "type": "handler", "parent": "M200", "left": "M211", "right": "M212", "external": None},
    "M220": {"name": "Output Handler", "level": 2, "type": "handler", "parent": "M200", "left": "M221", "right": "M222", "external": None},
    "M111": {"name": "YAML Config", "level": 3, "type": "interface", "parent": "M110", "left": None, "right": None, "external": "File I/O (YAML)"},
    "M112": {"name": "Log Writer", "level": 3, "type": "interface", "parent": "M110", "left": None, "right": None, "external": "File I/O (Log)"},
    "M121": {"name": "Excel Handler", "level": 3, "type": "interface", "parent": "M120", "left": None, "right": None, "external": "File I/O (Excel)"},
    "M122": {"name": "SQL Database", "level": 3, "type": "interface", "parent": "M120", "left": None, "right": None, "external": "SQLite/PostgreSQL"},
    "M211": {"name": "MCP Tools", "level": 3, "type": "interface", "parent": "M210", "left": None, "right": None, "external": "External API (LLM)"},
    "M212": {"name": "MCP Resources", "level": 3, "type": "interface", "parent": "M210", "left": None, "right": None, "external": "External API (Resources)"},
    "M221": {"name": "Web Interface", "level": 3, "type": "interface", "parent": "M220", "left": None, "right": None, "external": "HTTP (REST API)"},
    "M222": {"name": "PDF Generator", "level": 3, "type": "interface", "parent": "M220", "left": None, "right": None, "external": "File I/O (PDF)"},
}

def generate_prd(node_id: str, info: dict) -> str:
    external = f"**{info['external']}** - This is a LEAF node." if info['external'] else "**None** - Internal node"
    children = f"M{info['left']} (Left), M{info['right']} (Right)" if info['left'] else "None (Leaf node)"

    return f"""# {node_id} - {info['name']} PRD

## Overview
{info['name']} ({node_id}) is a {'leaf' if info['level'] == 3 else 'internal'} node at level {info['level']} of the BST architecture.

## Node Information
- **Node ID**: {node_id}
- **Level**: {info['level']} ({'Root' if info['level'] == 0 else 'Level ' + str(info['level']) if info['level'] < 3 else 'Leaf'})
- **Type**: {info['type'].title()}
- **Parent**: {info['parent'] or 'None'}
- **Children**: {children}

## External Interfaces
{external}

## Token Budget
- Configured in config/config.json
"""

def generate_plan(node_id: str, info: dict) -> str:
    return f"""# {node_id} - {info['name']} Implementation Plan

## Phase 1: Structure
- Implement {'LeafNode' if info['level'] == 3 else 'InternalNode'} base class
- Configure node properties

## Phase 2: Logic
- Implement process method
- Add action handlers

## Phase 3: Testing
- Write unit tests
- Verify token tracking
"""

def generate_todo(node_id: str, info: dict) -> str:
    return f"""# {node_id} - {info['name']} TODO

## Completed
- [x] Node structure
- [x] Process method
- [x] Unit tests framework

## Pending
- [ ] Enhanced error handling
- [ ] Performance optimization
"""

def generate_config(node_id: str, info: dict) -> dict:
    config = {
        "node_id": node_id,
        "name": info['name'],
        "level": info['level'],
        "type": info['type'],
        "parent": info['parent'],
    }
    if info['left']:
        config["children"] = {"left": info['left'], "right": info['right']}
    if info['external']:
        config["external_interface"] = info['external']
    return config

def main():
    project_root = Path(__file__).parent.parent

    for node_id, info in NODES.items():
        node_dir = project_root / "tree" / node_id

        # PRD
        prd_path = node_dir / "PRD.md"
        if not prd_path.exists():
            prd_path.write_text(generate_prd(node_id, info))
            print(f"Created {prd_path}")

        # PLAN
        plan_path = node_dir / "PLAN.md"
        if not plan_path.exists():
            plan_path.write_text(generate_plan(node_id, info))
            print(f"Created {plan_path}")

        # TODO
        todo_path = node_dir / "TODO.md"
        if not todo_path.exists():
            todo_path.write_text(generate_todo(node_id, info))
            print(f"Created {todo_path}")

        # Config
        config_path = node_dir / "config" / "config.json"
        if not config_path.exists():
            config_path.write_text(json.dumps(generate_config(node_id, info), indent=2))
            print(f"Created {config_path}")

        # README
        readme_path = node_dir / "README.md"
        if not readme_path.exists():
            readme_path.write_text(f"# {node_id} - {info['name']}\n\nSee PRD.md for details.\n")
            print(f"Created {readme_path}")

if __name__ == "__main__":
    main()
