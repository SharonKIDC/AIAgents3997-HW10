"""
M120 - Database Handler
Level 2 Internal Node: Data Persistence Coordination

Children:
- M121 (Excel Handler) - Left child
- M122 (SQL Database) - Right child

Responsibility: Coordinate data persistence across Excel and SQL storage
"""
from typing import Any, Dict, List
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.types import InternalNode, NodeConfig, NodeLevel, NodeType, NodeResult

# Import child node factories
from tree.M121.src.main import create_node as create_m121
from tree.M122.src.main import create_node as create_m122


class DatabaseHandlerNode(InternalNode):
    """
    M120 - Database Handler Internal Node

    Responsibility: Coordinate data persistence operations
    Children: M121 (Excel Handler), M122 (SQL Database)
    """

    def __init__(self):
        config = NodeConfig(
            node_id="M120",
            name="Database Handler",
            level=NodeLevel.LEVEL_2,
            node_type=NodeType.HANDLER,
            parent_id="M100",
            left_child_id="M121",
            right_child_id="M122",
            token_budget=20000,
            metadata={"role": "data_persistence"}
        )
        super().__init__(config)
        self._init_children()

    def _init_children(self):
        """Initialize child nodes."""
        self.left = create_m121()  # Excel Handler
        self.right = create_m122()  # SQL Database
        self.left.parent = self
        self.right.parent = self

    def process(self, input_data: Any) -> NodeResult:
        """
        Process data persistence request by coordinating children.

        Input format:
        {
            "action": "get_tenants" | "add_tenant" | "sync" | "import_excel" | "export_excel" | "query",
            "source": "excel" | "database" | "both",
            "data": {...}
        }
        """
        action = input_data.get("action", "get_tenants")
        source = input_data.get("source", "database")
        tokens_used = 10

        try:
            if action == "get_tenants":
                if source == "excel":
                    result = self.left.process({"action": "get_sheet", "path": "tenants.xlsx"})
                elif source == "database":
                    result = self.right.process({"action": "get_tenants"})
                else:  # both - merge results
                    excel_result = self.left.process({"action": "get_sheet", "path": "tenants.xlsx"})
                    db_result = self.right.process({"action": "get_tenants"})

                    tokens_used += excel_result.tokens_used + db_result.tokens_used

                    merged_data = {
                        "excel": excel_result.data if excel_result.success else [],
                        "database": db_result.data if db_result.success else [],
                    }

                    return NodeResult(
                        success=excel_result.success or db_result.success,
                        data=merged_data,
                        tokens_used=tokens_used,
                        node_id=self.node_id
                    )

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "add_tenant":
                tenant_data = input_data.get("data", {})

                # Add to database (primary storage)
                db_result = self.right.process({
                    "action": "add_tenant",
                    "data": tenant_data
                })

                # Optionally sync to Excel
                if input_data.get("sync_excel", True):
                    self.left.process({
                        "action": "add_row",
                        "path": "tenants.xlsx",
                        "data": tenant_data
                    })

                tokens_used += db_result.tokens_used + 20
                return NodeResult(
                    success=db_result.success,
                    data=db_result.data,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "import_excel":
                # Import data from Excel to database
                excel_path = input_data.get("path", "tenants.xlsx")

                excel_result = self.left.process({
                    "action": "get_sheet",
                    "path": excel_path
                })

                if not excel_result.success:
                    return NodeResult(
                        success=False,
                        error=f"Failed to read Excel: {excel_result.error}",
                        tokens_used=tokens_used + excel_result.tokens_used,
                        node_id=self.node_id
                    )

                imported = 0
                for row in excel_result.data:
                    self.right.process({
                        "action": "add_tenant",
                        "data": row
                    })
                    imported += 1

                tokens_used += excel_result.tokens_used + (imported * 20)
                return NodeResult(
                    success=True,
                    data={"imported": imported, "source": excel_path},
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "export_excel":
                # Export database to Excel
                output_path = input_data.get("path", "export.xlsx")

                db_result = self.right.process({"action": "get_tenants"})

                if not db_result.success:
                    return NodeResult(
                        success=False,
                        error=f"Failed to query database: {db_result.error}",
                        tokens_used=tokens_used + db_result.tokens_used,
                        node_id=self.node_id
                    )

                excel_result = self.left.process({
                    "action": "write",
                    "path": output_path,
                    "data": {"Sheet1": db_result.data}
                })

                tokens_used += db_result.tokens_used + excel_result.tokens_used
                return NodeResult(
                    success=excel_result.success,
                    data={"exported": len(db_result.data), "path": output_path},
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "sync":
                # Synchronize Excel and Database
                excel_result = self.left.process({"action": "get_sheet", "path": "tenants.xlsx"})
                db_result = self.right.process({"action": "get_tenants"})

                excel_ids = {t.get("id") for t in (excel_result.data or [])}
                db_ids = {t.get("id") for t in (db_result.data or [])}

                tokens_used += excel_result.tokens_used + db_result.tokens_used

                return NodeResult(
                    success=True,
                    data={
                        "excel_count": len(excel_ids),
                        "database_count": len(db_ids),
                        "in_sync": excel_ids == db_ids,
                        "only_in_excel": list(excel_ids - db_ids),
                        "only_in_db": list(db_ids - excel_ids)
                    },
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            elif action == "query":
                # Raw database query
                sql = input_data.get("sql", "")
                params = input_data.get("params", {})

                result = self.right.process({
                    "action": "query",
                    "sql": sql,
                    "params": params
                })

                tokens_used += result.tokens_used
                return NodeResult(
                    success=result.success,
                    data=result.data,
                    error=result.error,
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

            else:
                return NodeResult(
                    success=False,
                    error=f"Unknown action: {action}",
                    tokens_used=tokens_used,
                    node_id=self.node_id
                )

        except Exception as e:
            return NodeResult(
                success=False,
                error=str(e),
                tokens_used=tokens_used,
                node_id=self.node_id
            )

    def get_all_tenants(self, source: str = "database") -> List[Dict]:
        """Convenience method to get all tenants."""
        result = self.process({"action": "get_tenants", "source": source})
        return result.data if result.success else []

    def add_tenant(self, tenant: Dict, sync_excel: bool = True) -> bool:
        """Convenience method to add a tenant."""
        result = self.process({
            "action": "add_tenant",
            "data": tenant,
            "sync_excel": sync_excel
        })
        return result.success


# Factory function
def create_node() -> DatabaseHandlerNode:
    """Create and return M120 node instance."""
    return DatabaseHandlerNode()
