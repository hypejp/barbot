import gzip
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "JMnedict.xml.gz"
DATABASE = BASE / "jmnedict.sqlite"

if not SOURCE.is_file():
    raise SystemExit(f"Source not found: {SOURCE}")

if DATABASE.exists():
    raise SystemExit(f"Database already exists: {DATABASE}")

db = sqlite3.connect(str(DATABASE))

db.executescript("""
CREATE TABLE entries (
    id INTEGER PRIMARY KEY
);

CREATE TABLE spellings (
    entry_id INTEGER NOT NULL,
    spelling TEXT NOT NULL
);

CREATE TABLE readings (
    entry_id INTEGER NOT NULL,
    reading TEXT NOT NULL
);

CREATE TABLE translations (
    entry_id INTEGER NOT NULL,
    trans_no INTEGER NOT NULL,
    language TEXT NOT NULL,
    detail TEXT NOT NULL
);

CREATE TABLE name_types (
    entry_id INTEGER NOT NULL,
    trans_no INTEGER NOT NULL,
    name_type TEXT NOT NULL
);

CREATE TABLE cross_references (
    entry_id INTEGER NOT NULL,
    trans_no INTEGER NOT NULL,
    reference TEXT NOT NULL
);
""")

count = 0
xml_lang = "{http://www.w3.org/XML/1998/namespace}lang"

try:
    with gzip.open(SOURCE, "rb") as source:
        for _, elem in ET.iterparse(source, events=("end",)):
            if elem.tag != "entry":
                continue

            entry_id = int(elem.findtext("ent_seq"))
            db.execute(
                "INSERT INTO entries (id) VALUES (?)",
                (entry_id,),
            )

            for spelling in elem.findall("k_ele/keb"):
                if spelling.text:
                    db.execute(
                        "INSERT INTO spellings VALUES (?, ?)",
                        (entry_id, spelling.text),
                    )

            for reading in elem.findall("r_ele/reb"):
                if reading.text:
                    db.execute(
                        "INSERT INTO readings VALUES (?, ?)",
                        (entry_id, reading.text),
                    )

            for trans_no, trans in enumerate(elem.findall("trans"), 1):
                for name_type in trans.findall("name_type"):
                    if name_type.text:
                        db.execute(
                            "INSERT INTO name_types VALUES (?, ?, ?)",
                            (entry_id, trans_no, name_type.text),
                        )

                for detail in trans.findall("trans_det"):
                    if detail.text:
                        db.execute(
                            "INSERT INTO translations VALUES (?, ?, ?, ?)",
                            (
                                entry_id,
                                trans_no,
                                detail.get(xml_lang, "eng"),
                                detail.text,
                            ),
                        )

                for reference in trans.findall("xref"):
                    if reference.text:
                        db.execute(
                            "INSERT INTO cross_references VALUES (?, ?, ?)",
                            (entry_id, trans_no, reference.text),
                        )

            count += 1
            elem.clear()

    db.executescript("""
    CREATE INDEX idx_spellings ON spellings(spelling);
    CREATE INDEX idx_readings ON readings(reading);
    CREATE INDEX idx_translations ON translations(entry_id);
    CREATE INDEX idx_name_types ON name_types(entry_id);
    """)

    db.commit()

except Exception:
    db.rollback()
    db.close()
    DATABASE.unlink(missing_ok=True)
    raise

db.close()

print(f"Created: {DATABASE}")
print(f"Entries: {count:,}")
print(f"Size: {DATABASE.stat().st_size / 1024 / 1024:.1f} MB")
