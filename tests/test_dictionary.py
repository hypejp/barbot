"""barbotの辞書機能のユニットテスト。"""

import sys
import unittest
from pathlib import Path

DICTIONARY_DIR = Path(__file__).resolve().parents[1] / "dictionary"
sys.path.insert(0, str(DICTIONARY_DIR))

from search import lookup, lookup_sense


class TestDictionary(unittest.TestCase):

    def test_japanese_to_english(self):
        result = lookup("猫")
        self.assertIsNotNone(result)
        self.assertEqual(result["meaning"], "cat")

    def test_english_to_japanese(self):
        result = lookup("music")
        self.assertIsNotNone(result)
        self.assertEqual(result["meaning"], "[名詞] 音楽、楽譜、ミュージック")

    def test_sense_number(self):
        result = lookup_sense("猫", 6)
        self.assertIsNotNone(result)
        self.assertEqual(result["sense_no"], 6)
        self.assertEqual(
            result["meaning"],
            "bottom (submissive partner of a homosexual relationship)",
        )

    def test_english_sense_number(self):
        result = lookup_sense("think", 3)
        self.assertIsNotNone(result)
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["sense_no"], 3)
        self.assertIn("思う", result["meaning"])
        self.assertIsNone(lookup_sense("think", 4))

    def test_invalid_sense_number(self):
        self.assertIsNone(lookup_sense("猫", 99))

    def test_unknown_word(self):
        self.assertIsNone(lookup("xyzzyfoobar123"))



    def test_multiple_japanese_senses(self):
        result = lookup("濃い")
        self.assertIsNotNone(result)
        self.assertEqual(result["meaning"], "deep (colour)")
        self.assertEqual(
            result["senses"][:3],
            [
                "deep (colour)",
                "strong (flavour, smell, etc.)",
                "thick (consistency)",
            ],
        )

    def test_food_explanations(self):
        cases = {
            "餃子": ("gyoza", "Chinese-origin dumplings"),
            "ぎょうざ": ("gyoza", "Chinese-origin dumplings"),
            "焼売": ("shumai", "Chinese-style steamed dumplings"),
            "しゅうまい": ("shumai", "Chinese-style steamed dumplings"),
            "たこ焼き": ("takoyaki", "octopus"),
            "お好み焼き": ("okonomiyaki", "savory pancake"),
        }
        for word, (meaning, note) in cases.items():
            with self.subTest(word=word):
                result = lookup(word)
                self.assertIsNotNone(result)
                self.assertEqual(result["meaning"], meaning)
                self.assertIn(note, result["note"])

if __name__ == "__main__":
    unittest.main()
