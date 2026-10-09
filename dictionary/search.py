import sqlite3
import sys

from overrides import ENGLISH_OVERRIDES
from formatting import split_gloss
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "jmdict.sqlite"


def search(term):
    term = term.strip()
    if not term:
        return None

    with sqlite3.connect(str(DATABASE)) as db:
        if term.isascii():
            override = ENGLISH_OVERRIDES.get(term.lower())
            if override:
                return truncate_utf8(f"{term} → {override}")

            row = db.execute("""
                SELECT e.word, e.reading
                FROM english AS x
                JOIN entries AS e ON e.id = x.entry_id
                WHERE x.term = ?
                   OR x.term LIKE ?
                ORDER BY e.priority DESC
                LIMIT 1
            """, (term.lower(), term.lower() + " (%")).fetchone()

            if row:
                word, reading = row
                return truncate_utf8(f"{term} → {word}【{reading}】")

        else:
            row = db.execute("""
                SELECT e.word, e.reading, e.meaning
                FROM japanese AS j
                JOIN entries AS e ON e.id = j.entry_id
                WHERE j.term = ?
                ORDER BY
                    CASE WHEN e.word = ? THEN 1 ELSE 0 END DESC,
                    e.priority DESC
                LIMIT 1
            """, (term, term)).fetchone()

            if row:
                word, reading, meaning = row
                return truncate_utf8(f"{word}【{reading}】 - {meaning}")

    return None


def truncate_utf8(text, max_bytes=200):
    """UTF-8の文字を壊さずに文字列を短縮する。"""
    if len(text.encode("utf-8")) <= max_bytes:
        return text

    result = ""
    for char in text:
        if len((result + char + "…").encode("utf-8")) > max_bytes:
            break
        result += char

    return result + "…"


if __name__ == "__main__":
    for term in sys.argv[1:]:
        print(f"{term}: {search(term) or '見つかりません'}")


def lookup(term):
    """JMdictから検索結果を取得する。表示用の文章は作らない。"""
    term = term.strip()
    if not term:
        return None

    with sqlite3.connect(str(DATABASE)) as db:
        if term.isascii():
            override = ENGLISH_OVERRIDES.get(term.lower())
            if override:
                return {
                    "language": "en",
                    "word": term,
                    "meaning": (
                        override.split("【")[0]
                        if "【" in override
                        and override.split("【")[0] == override.split("【")[1].rstrip("】")
                        else override.replace("【", "(").replace("】", ")")
                    ),
                }

            row = db.execute("""
                SELECT e.word, e.reading
                FROM english AS x
                JOIN entries AS e ON e.id = x.entry_id
                WHERE x.term = ?
                   OR x.term LIKE ?
                ORDER BY e.priority DESC
                LIMIT 1
            """, (term.lower(), term.lower() + " (%")).fetchone()

            if row:
                word, reading = row
                return {
                    "language": "en",
                    "word": term,
                    "meaning": f"{word}({reading})",
                }

        else:
            row = db.execute("""
                SELECT e.word, e.reading, e.meaning
                FROM japanese AS j
                JOIN entries AS e ON e.id = j.entry_id
                WHERE j.term = ?
                ORDER BY
                    CASE WHEN e.word = ? THEN 1 ELSE 0 END DESC,
                    e.priority DESC
                LIMIT 1
            """, (term, term)).fetchone()

            if row:
                word, reading, meaning = row
                display_meaning, note = split_gloss(meaning)
                return {
                    "language": "ja",
                    "word": f"{word}({reading})",
                    "meaning": display_meaning,
                    "note": note,
                }

    return None
