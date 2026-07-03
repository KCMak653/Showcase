from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

Row = Dict[str, Any]
Filter = Tuple[str, str, Any]  # (column, op, value)

# Portable filter vocabulary shared by all DBIO implementations.
FILTER_OPS = ("eq", "neq", "gt", "gte", "lt", "lte", "in", "like", "ilike")


class DBIO(ABC):
    """
    Abstract base for table-scoped database I/O.

    Subclasses connect to a storage backend, bind a table, and expose a small
    read/write surface: query rows and replace the table contents in one shot.

    Filter tuples use logical ops from :data:`FILTER_OPS`. Each subclass maps
    those ops to its native query API internally.
    """

    @abstractmethod
    def authenticate(self, table: str, primary_key: str = "id") -> None:
        """
        Connect to the backend and bind this instance to a table.

        Args:
            table: Table name to read from and write to.
            primary_key: Column used to identify rows (e.g. for full-table clears).
        """
        ...

    @abstractmethod
    def get_data(
        self,
        cols: str,
        filters: Optional[Sequence[Filter]] = None,
    ) -> List[Row]:
        """
        Read rows from the bound table.

        Args:
            cols: Columns to select (e.g. "*" or "id, name").
            filters: Optional list of (column, op, value) conditions.
                ``op`` must be one of :data:`FILTER_OPS`.

        Returns:
            Matching rows as a list of dicts.
        """
        ...

    @abstractmethod
    def replace_table(self, data: Union[Row, Sequence[Row]]) -> None:
        """
        Replace all rows in the bound table with the given data.

        Clears existing rows, then inserts the new snapshot.

        Args:
            data: One row dict or a list of row dicts.
        """
        ...

    def _validate_filters(
        self,
        filters: Optional[Sequence[Filter]],
        ops_mapping: Dict[str, str],
    ) -> List[Filter]:
        """
        Validate filter ops against the shared vocabulary and backend mapping.

        Args:
            filters: Filter tuples to validate.
            ops_mapping: Subclass-specific logical-op → native-op mapping.

        Returns:
            A list of validated filters (empty if ``filters`` is None).
        """
        validated: List[Filter] = []
        for col, op, value in filters or []:
            if op not in FILTER_OPS:
                raise ValueError(
                    f"unsupported filter op {op!r}; "
                    f"expected one of {list(FILTER_OPS)}"
                )
            if op not in ops_mapping:
                raise ValueError(
                    f"filter op {op!r} is not supported by {type(self).__name__}"
                )
            validated.append((col, op, value))
        return validated
