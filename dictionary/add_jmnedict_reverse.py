"""Add an indexed English reverse lookup table to an existing JMnedict database."""

import re
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "jmnedict.sqlite"


def lookup_keys(detail):
    """Return normalized keys for an English translation."""
    detail = detail.strip()
    if not detail:
        return set()

    keys = {detail.casefold()}

    # Allow 'Islay' to match 'Islay (island)'.
    match = re.fullmatch(r"(.+?) \([^()]+\)", detail)
    if match:
        keys.add(match.group(1).casefold())

    return keys


def create_reverse_lookup(db):
    """Create and populate the indexed English reverse lookup table."""
    db.execute("""
        CREATE TABLE english_lookup (
            lookup_key TEXT NOT NULL,
            entry_id INTEGER NOT NULL
        )
    """)

    rows = db.execute("""
        SELECT entry_id, detail
        FROM translations
        WHERE language = 'eng'
    """)

    batch = []
    count = 0

    for entry_id, detail in rows:
        for key in lookup_keys(detail):
            batch.append((key, entry_id))

        if len(batch) >= 10000:
            db.executemany(
                "INSERT INTO english_lookup VALUES (?, ?)",
                batch,
            )
            count += len(batch)
            batch.clear()

    if batch:
        db.executemany(
            "INSERT INTO english_lookup VALUES (?, ?)",
            batch,
        )
        count += len(batch)

    db.execute("""
        CREATE INDEX idx_english_lookup
        ON english_lookup(lookup_key)
    """)

    return count


def main():
    if not DATABASE.is_file():
        raise SystemExit(f"Database not found: {DATABASE}")

    with sqlite3.connect(str(DATABASE)) as db:
        if db.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'english_lookup'"
        ).fetchone():
            raise SystemExit("english_lookup already exists")

        count = create_reverse_lookup(db)

    print(f"Created english_lookup: {count:,} rows")


if __name__ == "__main__":
    main()
