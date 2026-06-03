from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection

CREATE_TABLE_DEPENDENCIES: dict[str, list[str]] = {
    "triggerMessagesChannel": ["triggerMessages"],
    "tickets": ["ticketMessages"],
    "dynamicslowmode_messages": ["dynamicslowmode"],
    "report_evidence": ["reports"],
    "report_mod_actions": ["reports"],
}


def _dependency_batches(table_names: set[str]) -> list[set[str]]:
    to_create = set(table_names)
    created: set[str] = set()
    batches: list[set[str]] = []
    while to_create:
        batch = {
            name
            for name in to_create
            if all(dep in created or dep not in to_create for dep in CREATE_TABLE_DEPENDENCIES.get(name, []))
        }
        if not batch:
            raise RuntimeError(f"Cannot resolve table dependencies for: {to_create}")
        batches.append(batch)
        to_create -= batch
        created.update(batch)
    return batches


def ordered_table_names(table_names: set[str] | None = None) -> list[str]:
    from api import get_table_definitions

    names = set(table_names) if table_names is not None else set(get_table_definitions())
    batches = _dependency_batches(names)
    return [name for batch in batches for name in sorted(batch)]


def run_create_all_tables(connection: Connection) -> None:
    from api import get_table_definitions

    tables = get_table_definitions()
    for table_name in ordered_table_names(set(tables)):
        connection.execute(text(tables[table_name]))
