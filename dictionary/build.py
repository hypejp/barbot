import gzip
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

from priority import priority_score

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "JMdict_e.gz"
DATABASE = BASE / "jmdict.sqlite"

db = sqlite3.connect(str(DATABASE))

db.executescript("""
DROP TABLE IF EXISTS senses;
DROP TABLE IF EXISTS japanese;
DROP TABLE IF EXISTS english;
DROP TABLE IF EXISTS entries;

CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    reading TEXT NOT NULL,
    meaning TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE senses (
    entry_id INTEGER NOT NULL,
    sense_no INTEGER NOT NULL,
    gloss_no INTEGER NOT NULL,
    gloss TEXT NOT NULL,
    PRIMARY KEY (entry_id, sense_no, gloss_no)
);

CREATE TABLE japanese (
    term TEXT NOT NULL,
    entry_id INTEGER NOT NULL
);

CREATE TABLE english (
    term TEXT NOT NULL,
    entry_id INTEGER NOT NULL
);
""")

count = 0

with gzip.open(SOURCE, "rb") as f:
    for _, elem in ET.iterparse(f, events=("end",)):
        if elem.tag != "entry":
            continue

        entry_id = int(elem.findtext("ent_seq"))

        words = [
            e.text for e in elem.findall("k_ele/keb")
            if e.text
        ]
        readings = [
            e.text for e in elem.findall("r_ele/reb")
            if e.text
        ]

        senses = elem.findall("sense")
        meanings = [
            gloss.text
            for sense in senses
            for gloss in sense.findall("gloss")
            if gloss.text
        ]

        tags = [
            e.text
            for e in elem.findall("k_ele/ke_pri")
            + elem.findall("r_ele/re_pri")
            if e.text
        ]

        if readings and meanings:
            word = words[0] if words else readings[0]
            reading = readings[0]
            score = priority_score(set(tags))

            db.execute(
                """INSERT INTO entries
                   (id, word, reading, meaning, priority)
                   VALUES (?, ?, ?, ?, ?)""",
                (entry_id, word, reading, meanings[0], score)
            )

            for sense_no, sense in enumerate(senses, 1):
                glosses = [
                    gloss.text
                    for gloss in sense.findall("gloss")
                    if gloss.text
                ]
                for gloss_no, gloss in enumerate(glosses, 1):
                    db.execute(
                        "INSERT INTO senses VALUES (?, ?, ?, ?)",
                        (entry_id, sense_no, gloss_no, gloss)
                    )

            for term in set(words + readings):
                db.execute(
                    "INSERT INTO japanese VALUES (?, ?)",
                    (term, entry_id)
                )

            for meaning in set(meanings):
                db.execute(
                    "INSERT INTO english VALUES (?, ?)",
                    (meaning.lower(), entry_id)
                )

            count += 1

        elem.clear()

db.executescript("""
CREATE INDEX idx_japanese ON japanese(term);
CREATE INDEX idx_english ON english(term);
CREATE INDEX idx_priority ON entries(priority);
""")

db.commit()
db.close()

print(f"Created: {DATABASE}")
print(f"Entries: {count:,}")
print(f"Size: {DATABASE.stat().st_size / 1024 / 1024:.1f} MB")
