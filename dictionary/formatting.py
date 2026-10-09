"""JMdictの訳語を表示用に整える。元データは変更しない。"""

CONFIRMED_NOTES = {
    "cat (esp. the domestic cat, Felis catus)": (
        "cat",
        "esp. the domestic cat, Felis catus",
    ),
    "dog (Canis (lupus) familiaris)": (
        "dog",
        "Canis (lupus) familiaris",
    ),
}


def split_gloss(gloss):
    """確認済みの訳語だけを本文と補足に分ける。"""
    if gloss in CONFIRMED_NOTES:
        return CONFIRMED_NOTES[gloss]

    return gloss, None
