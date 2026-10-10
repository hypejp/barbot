"""FreeDict English-Japanese dictionary lookup."""

import re
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("freedict-eng-jpn.sqlite")

POS_LABELS = {
    "n": "名詞",
    "v": "動詞",
    "adj": "形容詞",
    "adv": "副詞",
    "pn": "固有名詞",
    "conjunction": "接続詞",
    "prep": "前置詞",
    "pron": "代名詞",
    "interjection": "間投詞",
}

POS_LABELS.update({
    "preposition": "前置詞",
    "pronoun": "代名詞",
    "determiner": "限定詞",
    "numeral": "数詞",
    "particle": "助詞",
    "article": "冠詞",
    "phraseologicalUnit": "慣用句",
    "proverb": "ことわざ",
    "prefix": "接頭辞",
    "suffix": "接尾辞",
    "postposition": "後置詞",
    "symbol": "記号",
})


MAX_BYTES = 180
MAX_LINES = 2

POS_PRIORITY = {
    "v": 0,
    "n": 1,
    "adj": 2,
    "adv": 3,
    "conjunction": 4,
    "pronoun": 5,
    "preposition": 6,
    "pn": 7,
}


def fetch_senses(word):
    """Retrieve translations grouped by entry and sense."""
    with sqlite3.connect(DATABASE) as db:
        rows = db.execute(
            """
            SELECT e.id, e.pos, s.sense_no,
                   s.definition, t.translation
            FROM entries e
            JOIN senses s ON s.entry_id = e.id
            JOIN translations t ON t.sense_id = s.id
            WHERE e.word = ? COLLATE NOCASE
            ORDER BY e.source_order,
                     s.sense_no,
                     t.translation_order
            """,
            (word,),
        ).fetchall()

    entries = {}

    for entry_id, pos, sense_no, definition, translation in rows:
        entry = entries.setdefault(
            entry_id, {"pos": pos, "senses": {}, "definitions": {}}
        )
        entry["senses"].setdefault(sense_no, []).append(translation)
        entry["definitions"][sense_no] = definition

    return list(entries.values())



UNCOMMON_LABELS = {"rare", "archaic", "obsolete"}


def is_uncommon_definition(definition):
    """Check usage labels at the beginning of a definition."""
    match = re.match(r"^\(([^)]*)\)", definition or "")
    if not match:
        return False

    labels = {
        label.strip().lower()
        for label in match.group(1).split(",")
    }
    return bool(labels & UNCOMMON_LABELS)


def prioritize_senses(entry):
    """Put uncommon senses last without changing their numbers."""
    senses = entry["senses"]
    definitions = entry.get("definitions", {})

    common = [
        number for number in senses
        if not is_uncommon_definition(definitions.get(number, ""))
    ]

    # 通常の語義があれば、珍しい語義は代表訳から除外する。
    # すべて珍しい語義の場合は、元の語義を使用する。
    selected = common if common else list(senses)
    return {number: senses[number] for number in selected}

def select_translations(senses, limit=3):
    """Choose sense representatives, then fill from the first sense."""
    selected = []
    seen = set()

    def add(value):
        if value and value not in seen and len(selected) < limit:
            seen.add(value)
            selected.append(value)

    # First pass: one representative from each sense.
    for translations in senses.values():
        if translations:
            add(translations[0])

    # Second pass: additional translations from the first sense.
    if senses and len(selected) < limit:
        first_sense = next(iter(senses.values()))
        for translation in first_sense:
            add(translation)

    return selected


def choose_translations(pos, senses):
    if pos == "conjunction" and senses:
        first = next(iter(senses.values()))
        return first[:3]

    return select_translations(senses)


def format_lines(word, groups):
    prefix = f"{word} → "
    lines = []
    current = prefix

    for pos, translations in groups:
        label = POS_LABELS.get(pos, pos)
        remaining = list(translations)

        while remaining:
            part = f"[{label}] " + "、".join(remaining)
            separator = " / " if current != prefix else ""
            candidate = current + separator + part

            if len(candidate.encode("utf-8")) <= MAX_BYTES:
                current = candidate
                break

            if current != prefix and len(lines) < MAX_LINES - 1:
                lines.append(current)
                current = prefix
                continue

            remaining.pop()

    if current != prefix:
        lines.append(current)

    return lines


def lookup(word, sense_no=None):
    word = word.strip()
    if not word:
        return None

    entries = fetch_senses(word)
    if not entries:
        return None

    grouped = {}

    for entry in entries:
        pos = entry["pos"]
        selected = grouped.setdefault(pos, [])

        if sense_no is not None:
            translations = entry["senses"].get(sense_no, [])
        else:
            translations = choose_translations(
                pos, prioritize_senses(entry)
            )

        for translation in translations:
            if translation not in selected:
                selected.append(translation)

    groups = [
        (pos, translations[:3])
        for pos, translations in grouped.items()
        if translations
    ]

    groups.sort(
        key=lambda item: POS_PRIORITY.get(item[0], 99)
    )

    if not groups:
        return None

    return format_lines(word, groups)


