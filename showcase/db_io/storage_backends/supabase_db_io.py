import os
from typing import Any, List, Optional, Sequence, Union

import supabase

from showcase.db_io.db_io import DBIO, Filter, Row


class SupabaseDBIO(DBIO):
    """
    Supabase/PostgREST implementation of :class:`DBIO`.

    Uses the Supabase Python client to read and write a single bound table.
    """

    # Logical op (FILTER_OPS) → PostgREST client method name.
    _OPS = {
        "eq": "eq",
        "neq": "neq",
        "gt": "gt",
        "gte": "gte",
        "lt": "lt",
        "lte": "lte",
        "in": "in_",
        "like": "like",
        "ilike": "ilike",
    }

    def authenticate(self, table: str, primary_key: str = "id") -> None:
        """Create a Supabase client and bind a table for subsequent operations."""
        url = os.environ["SUPABASE_URL"]
        api_key = os.environ["SUPABASE_KEY"]

        self.client = supabase.create_client(url, api_key)
        self.table = table
        self.primary_key = primary_key

    def get_data(
        self,
        cols: str,
        filters: Optional[Sequence[Filter]] = None,
    ) -> List[Row]:
        """Select rows from the bound table, optionally applying filters."""
        validated = self._validate_filters(filters, self._OPS)
        query = self.client.table(self.table).select(cols)
        query = self._apply_filters(query, validated)
        return query.execute().data

    def _apply_filters(self, query: Any, filters: Sequence[Filter]) -> Any:
        """Map logical filter ops to PostgREST query methods."""
        for col, op, value in filters:
            method = getattr(query, self._OPS[op])
            query = method(col, value)
        return query

    def replace_table(self, data: Union[Row, Sequence[Row]]) -> None:
        """Clear the bound table and insert the given row snapshot."""
        self._clear_table()
        self._insert_rows(data)

    def _insert_rows(self, data: Union[Row, Sequence[Row]]) -> None:
        """Insert one or more rows into the bound table."""
        rows = [data] if isinstance(data, dict) else list(data)
        response = self.client.table(self.table).insert(rows).execute()
        print("inserted:", response.data)

    def _upsert_rows(self, data: Union[Row, Sequence[Row]]) -> None:
        """Upsert one or more rows into the bound table."""
        rows = [data] if isinstance(data, dict) else list(data)
        response = self.client.table(self.table).upsert(rows).execute()
        print("upserted:", response.data)

    def _clear_table(self) -> None:
        """Delete all rows from the bound table."""
        self.client.table(self.table).delete().neq(self.primary_key, 0).execute()

    def _get_all_rows(self) -> List[Row]:
        """Return every row from the bound table."""
        return self.get_data(cols="*")


if __name__ == "__main__":
    from showcase.settings import load_env

    load_env()
    db = SupabaseDBIO()
    db.authenticate(table="test")
    db._upsert_rows({"id": 9, "num": 83})
    print(db.get_data(cols="*", filters=[("num", "gt", 81)]))
