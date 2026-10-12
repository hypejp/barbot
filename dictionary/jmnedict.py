"""JMnedict固有名詞辞書の検索。"""

import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "jmnedict.sqlite"


def lookup(term):
    """日本語の固有名詞を検索する。見つからなければNone。"""
    term = term.strip()
    if not term or term.isascii() or not DATABASE.is_file():
        return None

    with sqlite3.connect(str(DATABASE)) as db:
        row = db.execute("""
            SELECT s.entry_id, s.spelling, r.reading
            FROM spellings AS s
            JOIN readings AS r ON r.entry_id = s.entry_id
            WHERE s.spelling = ?
            ORDER BY s.entry_id
            LIMIT 1
        """, (term,)).fetchone()

        if not row:
            row = db.execute("""
                SELECT r.entry_id, COALESCE(s.spelling, r.reading),
                       r.reading
                FROM readings AS r
                LEFT JOIN spellings AS s ON s.entry_id = r.entry_id
                WHERE r.reading = ?
                ORDER BY r.entry_id
                LIMIT 1
            """, (term,)).fetchone()

        if not row:
            return None

        entry_id, spelling, reading = row

        translations = db.execute("""
            SELECT DISTINCT detail
            FROM translations
            WHERE entry_id = ? AND language = 'eng'
            ORDER BY trans_no
            LIMIT 3
        """, (entry_id,)).fetchall()

        if not translations:
            return None

        types = db.execute("""
            SELECT DISTINCT name_type
            FROM name_types
            WHERE entry_id = ?
            LIMIT 3
        """, (entry_id,)).fetchall()

    return {
        "language": "ja",
        "source": "jmnedict",
        "word": f"{spelling}({reading})",
        "meaning": " / ".join(item[0] for item in translations),
        "name_types": [item[0] for item in types],
    }
