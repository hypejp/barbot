"""JMnedict固有名詞辞書の検索。"""

import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "jmnedict.sqlite"


def lookup(term):
    """日本語の固有名詞を検索し、適切な候補と別の読みを返す。"""
    term = term.strip()
    if not term or term.isascii() or not DATABASE.is_file():
        return None

    with sqlite3.connect(str(DATABASE)) as db:
        rows = db.execute("""
            SELECT DISTINCT s.entry_id, s.spelling, r.reading
            FROM spellings AS s
            JOIN readings AS r ON r.entry_id = s.entry_id
            WHERE s.spelling = ?
            ORDER BY s.entry_id
        """, (term,)).fetchall()

        if not rows:
            rows = db.execute("""
                SELECT DISTINCT r.entry_id,
                       COALESCE(s.spelling, r.reading), r.reading
                FROM readings AS r
                LEFT JOIN spellings AS s ON s.entry_id = r.entry_id
                WHERE r.reading = ?
                ORDER BY r.entry_id
            """, (term,)).fetchall()

        if not rows:
            return None

        candidates = []
        for entry_id, spelling, reading in rows:
            translations = db.execute("""
                SELECT DISTINCT detail
                FROM translations
                WHERE entry_id = ? AND language = 'eng'
                ORDER BY trans_no
                LIMIT 3
            """, (entry_id,)).fetchall()

            if not translations:
                continue

            types = db.execute("""
                SELECT DISTINCT name_type
                FROM name_types
                WHERE entry_id = ?
                LIMIT 3
            """, (entry_id,)).fetchall()

            candidates.append({
                "spelling": spelling,
                "reading": reading,
                "meaning": " / ".join(item[0] for item in translations),
                "name_types": [item[0] for item in types],
            })

    if not candidates:
        return None

    priority = {
        "place name": 0,
        "railway station": 1,
        "full name of a particular person": 2,
        "family or surname": 3,
        "unclassified name": 9,
    }

    def score(candidate):
        return min(
            (priority.get(t, 5) for t in candidate["name_types"]),
            default=8,
        )

    candidates.sort(key=score)
    best = candidates[0]

    alternatives = []
    for candidate in candidates[1:]:
        shared_types = set(candidate["name_types"]) & set(best["name_types"])
        if shared_types and candidate["reading"] != best["reading"]:
            item = {
                "reading": candidate["reading"],
                "meaning": candidate["meaning"],
            }
            if item not in alternatives:
                alternatives.append(item)

    return {
        "language": "ja",
        "source": "jmnedict",
        "word": f"{best['spelling']}({best['reading']})",
        "meaning": best["meaning"],
        "name_types": best["name_types"],
        "alternatives": alternatives,
    }
