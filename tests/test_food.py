"""料理・食品の英語説明のテスト。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dictionary"))

from food import FOOD_DESCRIPTIONS, get_food_description


class TestFoodDescriptions(unittest.TestCase):

    def test_yakisoba(self):
        description = get_food_description("焼きそば")
        self.assertIn("stir-fried noodles", description)

    def test_takoyaki(self):
        description = get_food_description("たこ焼き")
        self.assertIn("octopus", description)

    def test_daifuku(self):
        description = get_food_description("大福")
        self.assertIn("rice cake", description)

    def test_unknown_word(self):
        self.assertIsNone(get_food_description("自転車"))

    def test_all_descriptions(self):
        self.assertGreaterEqual(len(FOOD_DESCRIPTIONS), 24)
        for word, description in FOOD_DESCRIPTIONS.items():
            with self.subTest(word=word):
                self.assertTrue(word)
                self.assertTrue(description)
                self.assertLessEqual(len(description), 150)


if __name__ == "__main__":
    unittest.main()
