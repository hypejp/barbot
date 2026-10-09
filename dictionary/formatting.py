"""JMdictの訳語を表示用に整える。元データは変更しない。"""

CONFIRMED_NOTES = {
    "gyoza": (
        "gyoza",
        "Chinese-origin dumplings, commonly pan-fried in Japan",
    ),
    "shumai": (
        "shumai",
        "Chinese-style steamed dumplings",
    ),
    "takoyaki": (
        "takoyaki",
        "Japanese snack made of batter balls filled with octopus",
    ),
    "okonomiyaki": (
        "okonomiyaki",
        "Japanese savory pancake with cabbage and other ingredients",
    ),
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
