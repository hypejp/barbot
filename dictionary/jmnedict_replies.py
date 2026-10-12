"""Generate natural English replies for JMnedict proper names."""

import random
import re

_last_template = {}

TEMPLATES = {
    "person": [
        "{english}{dates} was a Japanese historical figure.{extra}",
        "{english}{dates} was a figure in Japanese history.{extra}",
    ],
    "station": [
        "{name} ({english}) is a railway station in Japan.",
        "{english} is the English name for the Japanese railway station {name}.",
    ],
    "place": [
        "{name} is known as {english} in English.",
        "The English name for {name} is {english}.",
    ],
    "other": [
        "{name} is written as '{english}' in English.",
        "The English rendering of {name} is '{english}'.",
    ],
}


def parse_meaning(meaning):
    """Separate English name, dates, and additional information."""
    match = re.fullmatch(r"(.+?) \(([^()]*)\)(?:, (.*))?", meaning)

    if not match:
        return meaning, "", ""

    english, note, extra = match.groups()

    dates = re.fullmatch(
        r"(\d{4})(?:\.\d{1,2}\.\d{1,2})?"
        r"-(\d{4})(?:\.\d{1,2}\.\d{1,2})?",
        note,
    )

    if dates:
        years = f" ({dates.group(1)}-{dates.group(2)})"
    else:
        years = ""
        if note:
            extra = f"{note}; {extra}" if extra else note

    return english, years, extra or ""


def make_jmnedict_reply(result):
    """Create a conversational English reply from JMnedict data."""
    global _last_template

    word = result["word"]
    match = re.fullmatch(r"(.+)\((.+)\)", word)

    if match:
        name, reading = match.groups()
    else:
        name, reading = word, word

    english, dates, extra = parse_meaning(result["meaning"])
    types = result.get("name_types", [])

    if "full name of a particular person" in types:
        category = "person"
    elif "railway station" in types:
        category = "station"
    elif "place name" in types:
        category = "place"
    else:
        category = "other"

    extra_sentence = ""

    shogun = re.fullmatch(r"Shougun (\d{4})-(\d{4})", extra)
    if shogun:
        extra_sentence = (
            f" He served as shogun from "
            f"{shogun.group(1)} to {shogun.group(2)}."
        )
    elif extra:
        extra_sentence = f" Additional information: {extra}."

    templates = TEMPLATES[category]
    previous = _last_template.get(category)
    candidates = [t for t in templates if t != previous]
    template = random.choice(candidates)
    _last_template[category] = template

    reply = template.format(
        name=name,
        reading=reading,
        english=english,
        dates=dates,
        extra=extra_sentence,
    )

    alternatives = result.get("alternatives", [])
    if alternatives and "family or surname" in types and category == "other":
        variants = [(reading, english)] + [(item["reading"], item["meaning"]) for item in alternatives]
        readings = ", ".join(f"{r} ({e})" for r, e in variants[:3])
        return f"{name} is a Japanese surname. Possible readings include {readings}. 🍺"
    if alternatives:
        variants = ", ".join(
            f"{item['reading']} ({item['meaning']})"
            for item in alternatives[:2]
        )
        reply += f" Alternative readings include {variants}."

    return reply + " 🍺"
