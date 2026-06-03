"""Pydantic models for declarative SQL table definitions.

Provides ColumnDef, IndexDef, ForeignKeyDef, and TableDef to replace
raw SQL strings in get_table_definitions() with type-checked data classes
that can generate DDL automatically.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ColumnDef(BaseModel):
    """Definition of a single table column."""

    name: str
    sql_type: str
    primary_key: bool = False
    nullable: bool = True
    default: str | None = None
    auto_increment: bool = False
    comment: str | None = None

    def to_sql(self) -> str:
        """Render this column as a fragment of a CREATE TABLE statement."""
        parts = [f"  `{self.name}` {self.sql_type}"]
        if self.auto_increment:
            parts.append("AUTO_INCREMENT")
        if self.primary_key:
            parts.append("PRIMARY KEY")
        elif not self.nullable:
            parts.append("NOT NULL")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)


class IndexDef(BaseModel):
    """Definition of a table index."""

    name: str
    columns: list[str]  # column names, optionally with " DESC" suffix
    unique: bool = False
    index_type: str | None = None  # e.g. FULLTEXT, SPATIAL

    def to_sql(self) -> str:
        """Render this index definition.

        Columns may include a direction suffix ("DESC" or "ASC");
        pass them as part of the column string, e.g. "xp DESC" or "created_at ASC".
        """
        cols = ", ".join(f"`{c.split()[0]}`" + (f" {c.split()[1]}" if len(c.split()) > 1 else "") for c in self.columns)
        unique = "UNIQUE " if self.unique else ""
        name = "`" + self.name + "`" if not self.name.startswith("`") else self.name
        return f"  {unique}INDEX {name} ({cols})"


class ForeignKeyDef(BaseModel):
    """Definition of a foreign key constraint."""

    columns: list[str]
    ref_table: str
    ref_columns: list[str]
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"

    def to_sql(self) -> str:
        """Render this foreign key constraint."""
        cols = ", ".join(f"`{c}`" for c in self.columns)
        ref_cols = ", ".join(f"`{c}`" for c in self.ref_columns)
        return (
            f"  FOREIGN KEY ({cols}) "
            f"REFERENCES `{self.ref_table}` ({ref_cols}) "
            f"ON DELETE {self.on_delete} ON UPDATE {self.on_update}"
        )


class TableDef(BaseModel):
    """Definition of a database table with optional metadata."""

    name: str
    columns: list[ColumnDef]
    engine: str = "InnoDB"
    charset: str = "utf8mb4"
    primary_key: list[str] = Field(default_factory=list)  # Composite PK column names
    indices: list[IndexDef] = Field(default_factory=list)
    foreign_keys: list[ForeignKeyDef] = Field(default_factory=list)
    comment: str | None = None

    def _get_pk_col_names(self) -> list[str]:
        """Return the list of primary key column names."""
        # If explicit composite PK is set, use it
        if self.primary_key:
            return self.primary_key
        # Otherwise collect single-column PKs
        return [c.name for c in self.columns if c.primary_key]

    def to_sql(self, if_not_exists: bool = True) -> str:
        """Generate a CREATE TABLE statement from this model."""
        parts = [f"CREATE TABLE{' IF NOT EXISTS' if if_not_exists else ''} `{self.name}` ("]

        col_lines = [c.to_sql() for c in self.columns]
        extra_lines: list[str] = []

        pk_names = self._get_pk_col_names()

        if pk_names:
            col_lines = []
            for c in self.columns:
                sql = c.to_sql()
                if c.name in pk_names:
                    sql = sql.replace(" PRIMARY KEY", "")
                col_lines.append(sql)
            pk_str = ", ".join(f"`{n}`" for n in pk_names)
            extra_lines.append(f"  PRIMARY KEY ({pk_str})")

        extra_lines.extend(idx.to_sql() for idx in self.indices)
        extra_lines.extend(fk.to_sql() for fk in self.foreign_keys)

        all_lines = col_lines + extra_lines
        parts.append(",\n".join(all_lines))
        parts.append(f") ENGINE={self.engine}")

        if self.charset:
            parts.append(f"DEFAULT CHARSET={self.charset}")

        if self.comment:
            parts.append(f"COMMENT='{self.comment}'")

        return "\n".join(parts)


# ── Builder helpers ──────────────────────────────────────────────────────────────


def col(
    name: str,
    sql_type: str,
    *,
    pk: bool = False,
    nullable: bool = True,
    default: str | None = None,
    ai: bool = False,
    comment: str | None = None,
) -> ColumnDef:
    """Shortcut factory for ColumnDef."""
    return ColumnDef(
        name=name,
        sql_type=sql_type,
        primary_key=pk,
        nullable=nullable,
        default=default,
        auto_increment=ai,
        comment=comment,
    )


def idx(name: str, *columns: str, unique: bool = False) -> IndexDef:
    """Shortcut factory for IndexDef."""
    return IndexDef(name=name, columns=list(columns), unique=unique)


def fk(columns: list[str], ref_table: str, ref_columns: list[str]) -> ForeignKeyDef:
    """Shortcut factory for ForeignKeyDef."""
    return ForeignKeyDef(columns=columns, ref_table=ref_table, ref_columns=ref_columns)
