def priority_score(tags):
    """JMdictの優先度タグを検索用スコアに変換する。"""
    score = 0

    for tag in tags:
        if tag in ("ichi1", "news1", "spec1"):
            score += 100
        elif tag in ("ichi2", "news2", "spec2"):
            score += 50
        elif tag.startswith("nf") and tag[2:].isdigit():
            score += max(0, 50 - int(tag[2:]))

    return score
