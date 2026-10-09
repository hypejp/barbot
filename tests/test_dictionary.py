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
        self.assertEqual(result["meaning"], "音楽(おんがく)")

    def test_sense_number(self):
        result = lookup_sense("猫", 6)
        self.assertIsNotNone(result)
        self.assertEqual(result["sense_no"], 6)
        self.assertEqual(
            result["meaning"],
            "bottom (submissive partner of a homosexual relationship)",
        )

    def test_invalid_sense_number(self):
        self.assertIsNone(lookup_sense("猫", 99))

    def test_unknown_word(self):
        self.assertIsNone(lookup("xyzzyfoobar123"))


if __name__ == "__main__":
    unittest.main()
