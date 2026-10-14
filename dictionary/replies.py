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



def natural_japanese_meaning(meaning):
    """FreeDictの品詞付き訳語を読みやすく整える。"""
    import re

    groups = re.findall(r"\[[^\]]+\]\s*([^/]+)", meaning)
    if not groups:
        return meaning

    translations = []
    for group in groups:
        for item in group.split("、"):
            item = item.strip()
            if item and item not in translations:
                translations.append(item)

    if not translations:
        return meaning

    first = translations[0]
    others = translations[1:3]

    if others:
        quoted = "や".join(f"『{item}』" for item in others)
        return f"『{first}』という意味だよ。{quoted}という意味でも使われるね"

    return f"『{first}』という意味だよ"

def make_reply(word, meaning, language):
    """直前と異なるセリフを選んで返す。"""
    if language == "ja":
        templates = ENGLISH_TEMPLATES
    elif language == "en":
        templates = JAPANESE_TEMPLATES
    else:
        raise ValueError(f"Unsupported language: {language}")

    if language == "en" and meaning.startswith("["):
        return f"{word}は{natural_japanese_meaning(meaning)}。🍺"

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



def unique_translations(translations):
    """表記違いのカタカナ語をまとめ、代表訳を残す。"""
    import re

    result = []
    seen = set()

    for translation in translations:
        key = translation

        # カタカナ語の末尾の長音の有無だけを同一視する。
        if re.fullmatch(r"[ァ-ヶー]+", translation):
            key = translation.rstrip("ー")

        if key not in seen:
            seen.add(key)
            result.append(translation)

    return result


def make_structured_japanese_reply(word, entries):
    """FreeDictの品詞・語義を使って自然な日本語の説明を作る。"""
    from freedict import POS_LABELS, POS_PRIORITY, prioritize_senses
    from overrides import TRANSLATION_EXCLUSIONS

    exclusions = TRANSLATION_EXCLUSIONS.get(word.lower(), set())
    groups = []
    extra_meaning = None
    for entry in entries:
        pos = entry["pos"]
        senses = prioritize_senses(entry)
        if not senses:
            continue

        # 原則として第1語義の代表訳を優先する。
        first_sense = next(iter(senses.values()), [])
        translations = [
            t for t in unique_translations(first_sense)
            if t not in exclusions
        ][:2]

        # 除外設定がある単語では、別の語義も1つだけ確認する。
        if exclusions and extra_meaning is None:
            for other_sense in list(senses.values())[1:]:
                candidates = [
                    t for t in unique_translations(other_sense)
                    if t not in exclusions and t not in translations
                ]
                if candidates:
                    extra_meaning = candidates[0]
                    break

        # 形容詞は別の語義が重要な意味を持つことがある。
        if pos == "adj" and len(senses) > 1:
            second_sense = list(senses.values())[1]
            if second_sense and second_sense[0] not in translations:
                translations.append(second_sense[0])

        if not translations:
            continue

        label = POS_LABELS.get(pos, pos)

        # 同じ品詞の項目を統合し、訳語の重複を除く。
        existing = next((g for g in groups if g[0] == pos), None)
        if existing is not None:
            for translation in translations:
                if translation not in existing[2]:
                    existing[2].append(translation)
        else:
            groups.append((pos, label, translations))

    if not groups:
        return None

    # FreeDict本体と同じ品詞の優先順位を使用する。
    groups.sort(key=lambda g: POS_PRIORITY.get(g[0], 99))

    # 先に説明した訳語は、別の品詞で繰り返さない。
    seen = set()
    unique_groups = []
    for pos, label, translations in groups:
        unique = [t for t in translations if t not in seen]
        limit = 3 if pos == "adj" else 2
        selected = unique[:limit]
        if selected:
            seen.update(selected)
            quoted = "や".join(f"『{t}』" for t in selected)
            unique_groups.append((pos, label, quoted))

    groups = unique_groups

    if len(groups) == 1:
        reply = f"{word}は{groups[0][2]}という意味だよ。"
        if extra_meaning and extra_meaning not in seen:
            reply += f"『{extra_meaning}』を指すこともあるよ。"
        return reply + "🍺"

    descriptions = [
        f"{label}では{quoted}"
        for _, label, quoted in groups[:3]
    ]

    return f"{word}は" + "、".join(descriptions) + "という意味だよ。🍺"

def make_dictionary_replies(result):
    """検索結果からIRC送信用のメッセージ一覧を作る。"""
    if result is None:
        return []

    if result.get("source") == "jmnedict":
        from jmnedict_replies import make_jmnedict_reply
        return [make_jmnedict_reply(result)]

    if result.get("source") == "jmnedict_reverse":
        word = result["word"]
        candidates = result["candidates"]
        total = result["total_candidates"]

        names = "、".join(f"『{item['spelling']}』" for item in candidates)

        if total == 1:
            return [f"{word}は日本語で{names}と表記されるよ。🍺"]

        return [
            f"{word}の日本語表記には{names}などがあるよ。"
            f"(候補{total}件) 🍺"
        ]

    if result["language"] == "en" and result.get("entries"):
        first_line = make_structured_japanese_reply(
            result["word"],
            result["entries"],
        )
    else:
        first_line = None

    if first_line is None:
        senses = result.get("senses", [])
        if result["language"] == "ja" and len(senses) > 1:
            meanings = ", ".join(senses[:3])
            first_line = (
                f'{result["word"]}: {meanings}. 🍺'
            )
        else:
            first_line = make_reply(
                result["word"],
                result["meaning"],
                result["language"],
            )

    messages = [first_line]

    # 口語・俗語の補足説明。FreeDictとJMdictの両方に対応。
    if result["language"] == "en":
        from overrides import SLANG_NOTES

        slang = SLANG_NOTES.get(result["word"].lower())
        if slang:
            parts = []

            meanings = slang.get("meanings", [])
            if meanings:
                quoted = "や".join(f"『{m}』" for m in meanings)
                parts.append(f"{slang['label']}では{quoted}")

            verbs = slang.get("verb", [])
            if verbs:
                quoted = "や".join(f"『{v}』" for v in verbs)
                parts.append(f"動詞では{quoted}")

            if parts:
                messages.append(
                    "補足: " + "、".join(parts) + "という意味でも使うよ。"
                )

    note = result.get("note")
    if note:
        if (
            result["language"] == "ja"
            and result["meaning"] in {"gyoza", "shumai", "takoyaki", "okonomiyaki"}
            and len(result.get("senses", [])) <= 1
        ):
            messages = [
                f'{result["word"]}: {result["meaning"]} ({note}). 🍺'
            ]
        else:
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
