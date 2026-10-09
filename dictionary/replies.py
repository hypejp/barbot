import random

JAPANESE_TEMPLATES = [
    "{word}は日本語で『{meaning}』って意味だよ。",
    "{word}なら『{meaning}』って訳せるよ。",
    "{word}は『{meaning}』のことだね。",
    "{word}? 日本語では『{meaning}』だね。",
    "{word}は日本語で『{meaning}』だよ。🍺",
]

ENGLISH_TEMPLATES = [
    '"{word}" means "{meaning}" in English.',
    'You can translate "{word}" as "{meaning}".',
    '"{word}"? That would be "{meaning}" in English.',
    'In English, "{word}" can mean "{meaning}".',
    '"{word}" is "{meaning}" in English. 🍺',
]


_last_template = {}


def make_reply(word, meaning, language):
    """直前と異なるセリフを選んで返す。"""
    if language == "ja":
        templates = ENGLISH_TEMPLATES
    elif language == "en":
        templates = JAPANESE_TEMPLATES
    else:
        raise ValueError(f"Unsupported language: {language}")

    previous = _last_template.get(language)
    candidates = [t for t in templates if t != previous]
    template = random.choice(candidates)

    _last_template[language] = template
    return template.format(word=word, meaning=meaning)


JAPANESE_NOT_FOUND = [
    "わからないな、その言葉は。",
    "うーん、その言葉は知らないな。",
    "ごめん、それは辞書に載ってないみたい。",
    "その言葉は初耳だなあ。",
    "知らない言葉だね。勉強しておくよ。🍺",
]

ENGLISH_NOT_FOUND = [
    "Hmm, I don't know that word.",
    "Sorry, I couldn't find that one.",
    "That's a new one to me.",
    "I can't find that in my dictionary.",
    "You got me there! 🍺",
]


def make_not_found_reply(language):
    """辞書に見つからなかった場合のセリフを返す。"""
    if language == "ja":
        templates = JAPANESE_NOT_FOUND
    elif language == "en":
        templates = ENGLISH_NOT_FOUND
    else:
        raise ValueError(f"Unsupported language: {language}")

    key = f"not_found_{language}"
    previous = _last_template.get(key)
    candidates = [t for t in templates if t != previous]
    template = random.choice(candidates)

    _last_template[key] = template
    return template


def make_dictionary_replies(result):
    """検索結果からIRC送信用のメッセージ一覧を作る。"""
    if result is None:
        return []

    first_line = make_reply(
        result["word"],
        result["meaning"],
        result["language"],
    )

    messages = [first_line]

    note = result.get("note")
    if note:
        label = "Note" if result["language"] == "ja" else "補足"
        messages.append(f"{label}: {note}")

    return messages


SENSE_JAPANESE_TEMPLATES = [
    "{word}の{number}番目の意味は『{meaning}』だよ。",
    "{word}の{number}番目なら『{meaning}』だね。",
    "{word}の{number}番目は『{meaning}』って意味だよ。",
    "{word}? {number}番目の意味は『{meaning}』だね。",
    "{word}の{number}番目は『{meaning}』だよ。🍺",
]

SENSE_ENGLISH_TEMPLATES = [
    'The {ordinal} meaning of "{word}" is "{meaning}".',
    'For "{word}", meaning number {number} is "{meaning}".',
    'Meaning {number} of "{word}" is "{meaning}".',
    'The {ordinal} definition of "{word}" is "{meaning}".',
    '"{word}" has "{meaning}" as its {ordinal} meaning. 🍺',
]


def make_sense_reply(result):
    """語義番号指定の返答を翻訳先の言語で生成する。"""
    language = result["language"]
    number = result["sense_no"]

    if language == "en":
        templates = SENSE_JAPANESE_TEMPLATES
    elif language == "ja":
        templates = SENSE_ENGLISH_TEMPLATES
    else:
        raise ValueError(f"Unsupported language: {language}")

    key = f"sense_{language}"
    previous = _last_template.get(key)
    candidates = [t for t in templates if t != previous]
    template = random.choice(candidates)
    _last_template[key] = template

    suffix = (
        "th" if number % 100 in (11, 12, 13)
        else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )

    return template.format(
        word=result["word"],
        meaning=result["meaning"],
        number=number,
        ordinal=f"{number}{suffix}",
    )
