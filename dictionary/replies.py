import random

JAPANESE_TEMPLATES = [
    "{word}は英語で『{meaning}』って意味だよ。",
    "{word}なら英語で『{meaning}』って訳せるよ。",
    "{word}は『{meaning}』のことだね。",
    "{word}? 英語では『{meaning}』だね。",
    "{word}は英語で『{meaning}』だよ。🍺",
]

ENGLISH_TEMPLATES = [
    '"{word}" means "{meaning}" in Japanese.',
    'You can translate "{word}" as "{meaning}".',
    '"{word}"? That would be "{meaning}" in Japanese.',
    'In Japanese, "{word}" can mean "{meaning}".',
    '"{word}" is "{meaning}" in Japanese. 🍺',
]


_last_template = {}


def make_reply(word, meaning, language):
    """直前と異なるセリフを選んで返す。"""
    if language == "ja":
        templates = JAPANESE_TEMPLATES
    elif language == "en":
        templates = ENGLISH_TEMPLATES
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
        messages.append(f"補足: {note}")

    return messages
