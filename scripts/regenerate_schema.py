"""
Regenerate SCHEMA.md from the local Charvak database.

Usage:
    python scripts/regenerate_schema.py

Requires:
    DATABASE_URL env var, or defaults to postgresql://postgres:dev@localhost:5432/vouchai
"""
import io
import os
import sys
from datetime import datetime

import psycopg2

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/vouchai")


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # All charvak_* tables
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE 'charvak_%'
        ORDER BY table_name
    """)
    tables = [r[0] for r in cur.fetchall()]

    # Columns
    cur.execute("""
        SELECT table_name, column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name LIKE 'charvak_%'
        ORDER BY table_name, ordinal_position
    """)
    schema = {}
    for tname, cname, dtype, nullable, default in cur.fetchall():
        schema.setdefault(tname, []).append({
            "column": cname,
            "type": dtype,
            "nullable": nullable,
            "default": default,
        })

    # Indexes
    cur.execute("""
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public' AND tablename LIKE 'charvak_%'
        ORDER BY tablename, indexname
    """)
    indexes = {}
    for tname, iname in cur.fetchall():
        indexes.setdefault(tname, []).append(iname)

    # Build markdown
    out = []
    out.append("# Charvak Database Schema")
    out.append("")
    out.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}")
    out.append(f"**Total tables:** {len(tables)}")
    out.append("")
    out.append("**Purpose:** Complete snapshot of every `charvak_*` table.")
    out.append("Re-generate with: `python scripts/regenerate_schema.py`")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Table Index")
    out.append("")
    for t in tables:
        anchor = t.replace("_", "-").lower()
        out.append(f"- [{t}](#{anchor})")
    out.append("")
    out.append("---")
    out.append("")

    for t in tables:
        out.append(f"## {t}")
        out.append("")
        if t in schema:
            out.append("| Column | Type | Nullable | Default |")
            out.append("|---|---|---|---|")
            for col in schema[t]:
                d = col["default"]
                if d and len(d) > 40:
                    d = d[:37] + "..."
                d = (d or "").replace("|", "\\|")
                out.append(f"| {col['column']} | {col['type']} | {col['nullable']} | {d} |")
            out.append("")
        if t in indexes:
            out.append("**Indexes:**")
            out.append("")
            for iname in indexes[t]:
                out.append(f"- `{iname}`")
            out.append("")
        out.append("---")
        out.append("")

    with io.open("SCHEMA.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))

    print(f"Generated SCHEMA.md with {len(tables)} tables")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
