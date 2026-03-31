"""
Fallback in-memory database populated from clean_dump.sql.

Used when SUPABASE_URL / SUPABASE_SERVICE_KEY are absent or the Supabase
service is unreachable.  Implements the same chainable query interface as the
supabase-py client so the routers need no changes.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DUMP_PATH = Path(__file__).parent.parent / "clean_dump.sql"

def _parse_dump() -> dict[str, list[dict]]:
    """Read clean_dump.sql and return {table_name: [row_dict, ...]}."""
    try:
        text = DUMP_PATH.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, ValueError):
        return {}

    tables: dict[str, list[dict]] = {}

    # Match each COPY block:
    #   COPY public.tablename (col, ...) FROM stdin;\n<tab-separated rows>\n\.
    pattern = re.compile(
        r"COPY\s+public\.(\w+)\s+\(([^)]+)\)\s+FROM\s+stdin;\r?\n(.*?)\r?\n\\\.(?:\r?\n|$)",
        re.DOTALL | re.IGNORECASE,
    )

    for m in pattern.finditer(text):
        table_name = m.group(1)
        cols = [c.strip() for c in m.group(2).split(",")]
        block = m.group(3).strip()

        rows: list[dict] = []
        for line in block.splitlines():
            if not line.strip():
                continue
            values = line.split("\t")
            row: dict[str, Any] = {}
            for col, raw in zip(cols, values):
                v = raw.strip()
                if v == "\\N":
                    row[col] = None
                elif v == "t":
                    row[col] = True
                elif v == "f":
                    row[col] = False
                else:
                    row[col] = v
            rows.append(row)

        tables[table_name] = rows

    return tables



class _Result:
    __slots__ = ("data",)

    def __init__(self, data: list[dict]) -> None:
        self.data = data



class _QueryBuilder:
    def __init__(self, tables: dict[str, list[dict]], table_name: str) -> None:
        self._tables = tables
        self._table_name = table_name
        self._op = "select"
        self._filters: list[tuple[str, Any]] = []
        self._payload: Any = None
        self._order_field: str | None = None
        # Supabase join syntax: "project_id, projects(*)" → join_table = "projects"
        self._join_table: str | None = None


    def select(self, columns: str = "*") -> "_QueryBuilder":
        self._op = "select"
        m = re.search(r"(\w+)\(\*\)", columns)
        if m:
            self._join_table = m.group(1)
        return self

    def eq(self, field: str, value: Any) -> "_QueryBuilder":
        self._filters.append((field, value))
        return self

    def order(self, field: str) -> "_QueryBuilder":
        self._order_field = field
        return self

    def limit(self, n: int) -> "_QueryBuilder":  # noqa: ARG002
        return self

    def insert(self, data: dict | list[dict]) -> "_QueryBuilder":
        self._op = "insert"
        self._payload = data if isinstance(data, list) else [data]
        return self

    def update(self, data: dict) -> "_QueryBuilder":
        self._op = "update"
        self._payload = data
        return self

    def delete(self) -> "_QueryBuilder":
        self._op = "delete"
        return self


    def execute(self) -> _Result:
        if self._op == "select":
            return self._do_select()
        if self._op == "insert":
            return self._do_insert()
        if self._op == "update":
            return self._do_update()
        if self._op == "delete":
            return self._do_delete()
        return _Result([])

    def _matches(self, row: dict) -> bool:
        for field, value in self._filters:
            rv = row.get(field)
            if rv != value and str(rv) != str(value):
                return False
        return True

    def _do_select(self) -> _Result:
        rows = [r for r in self._tables.get(self._table_name, []) if self._matches(r)]

        if self._order_field:
            rows.sort(key=lambda r: r.get(self._order_field) or "")

        if self._join_table:
            # e.g. "projects(*)" on employee_project_selections
            # FK column: strip trailing 's' from join table name, append '_id'
            fk_col = self._join_table.rstrip("s") + "_id"
            related_map = {r["id"]: r for r in self._tables.get(self._join_table, [])}
            enriched = []
            for row in rows:
                r = dict(row)
                r[self._join_table] = related_map.get(r.get(fk_col))
                enriched.append(r)
            rows = enriched

        return _Result(rows)

    def _do_insert(self) -> _Result:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f+00")
        inserted = []
        table = self._tables.setdefault(self._table_name, [])
        for record in self._payload:
            row = dict(record)
            row.setdefault("id", str(uuid.uuid4()))
            row.setdefault("created_at", now)
            if self._table_name == "employees":
                row.setdefault("updated_at", now)
            elif self._table_name == "employee_project_selections":
                row.setdefault("selected_at", now)
            table.append(row)
            inserted.append(row)
        return _Result(inserted)

    def _do_update(self) -> _Result:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f+00")
        table = self._tables.get(self._table_name, [])
        updated = []
        for i, row in enumerate(table):
            if self._matches(row):
                merged = {**row, **self._payload}
                if self._table_name == "employees":
                    merged["updated_at"] = now
                table[i] = merged
                updated.append(merged)
        return _Result(updated)

    def _do_delete(self) -> _Result:
        table = self._tables.get(self._table_name, [])
        self._tables[self._table_name] = [r for r in table if not self._matches(r)]
        return _Result([])


class FallbackClient:
    """Drop-in replacement for the supabase-py Client when Supabase is unavailable."""

    def __init__(self) -> None:
        self._tables = _parse_dump()

    def table(self, name: str) -> _QueryBuilder:
        return _QueryBuilder(self._tables, name)
