import sqlite3
import sys

from overrides import ENGLISH_OVERRIDES, JAPANESE_NAME_ALIASES
from formatting import split_gloss
from freedict import lookup as freedict_lookup
from freedict import fetch_senses as freedict_fetch_senses
from jmnedict import lookup as jmnedict_lookup
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
            lines = freedict_lookup(term)
            if lines:
                meanings = [
                    line.removeprefix(f"{term} → ")
                    for line in lines
                ]
                return {
                    "language": "en",
                    "word": term,
                    "meaning": " / ".join(meanings),
                    "entries": freedict_fetch_senses(term),
                }

            # FreeDictにない英単語はJMdictから完全一致で補完する。
            rows = db.execute("""
                SELECT DISTINCT e.word
                FROM english AS x
                JOIN entries AS e ON e.id = x.entry_id
                WHERE x.term = ? COLLATE NOCASE
                ORDER BY e.priority DESC
                LIMIT 3
            """, (term,)).fetchall()

            if rows:
                translations = list(dict.fromkeys(word for (word,) in rows))
                return {
                    "language": "en",
                    "word": term,
                    "meaning": "、".join(translations),
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

    normalized = JAPANESE_NAME_ALIASES.get(term, term)
    result = jmnedict_lookup(normalized)
    if result and normalized != term:
        result["word"] = f"{term}({term})"
    return result


def lookup_sense(term, sense_no):
    """日本語の見出し語から指定番号の語義を取得する。"""
    term = term.strip()
    if not term or sense_no < 1:
        return None

    if term.isascii():
        lines = freedict_lookup(term, sense_no)
        if not lines:
            return None

        meanings = [
            line.removeprefix(f"{term} → ")
            for line in lines
        ]
        return {
            "language": "en",
            "word": term,
            "sense_no": sense_no,
            "meaning": " / ".join(meanings),
        }

    with sqlite3.connect(str(DATABASE)) as db:
        row = db.execute("""
            SELECT e.id, e.word, e.reading
            FROM japanese AS j
            JOIN entries AS e ON e.id = j.entry_id
            WHERE j.term = ?
            ORDER BY
                CASE WHEN e.word = ? THEN 1 ELSE 0 END DESC,
                e.priority DESC
            LIMIT 1
        """, (term, term)).fetchone()

        if not row:
            return None

        entry_id, word, reading = row
        glosses = db.execute("""
            SELECT gloss
            FROM senses
            WHERE entry_id = ? AND sense_no = ?
            ORDER BY gloss_no
        """, (entry_id, sense_no)).fetchall()

        if not glosses:
            return None

        return {
            "language": "ja",
            "word": f"{word}({reading})",
            "sense_no": sense_no,
            "meaning": "; ".join(gloss for (gloss,) in glosses),
        }
