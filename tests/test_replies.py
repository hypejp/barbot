"""barbotの辞書返答機能のユニットテスト。"""

import sys
import unittest
from pathlib import Path

DICTIONARY_DIR = Path(__file__).resolve().parents[1] / "dictionary"
sys.path.insert(0, str(DICTIONARY_DIR))

from replies import (
    ENGLISH_NOT_FOUND,
    JAPANESE_NOT_FOUND,
    make_dictionary_replies,
    make_not_found_reply,
    make_reply,
)


class TestDictionaryReplies(unittest.TestCase):

    def test_japanese_reply(self):
        reply = make_reply("猫(ねこ)", "cat", "ja")
        self.assertIn("猫(ねこ)", reply)
        self.assertIn("cat", reply)

    def test_english_reply(self):
        reply = make_reply("music", "音楽(おんがく)", "en")
        self.assertIn("music", reply)
        self.assertIn("音楽(おんがく)", reply)

    def test_reply_with_note(self):
        result = {
            "language": "ja",
            "word": "猫(ねこ)",
            "meaning": "cat",
            "note": "esp. the domestic cat, Felis catus",
        }
        messages = make_dictionary_replies(result)
        self.assertEqual(len(messages), 2)
        self.assertEqual(
            messages[1],
            "補足: esp. the domestic cat, Felis catus",
        )

    def test_reply_without_note(self):
        result = {
            "language": "en",
            "word": "music",
            "meaning": "音楽(おんがく)",
        }
        self.assertEqual(len(make_dictionary_replies(result)), 1)

    def test_not_found_replies(self):
        self.assertIn(make_not_found_reply("ja"), JAPANESE_NOT_FOUND)
        self.assertIn(make_not_found_reply("en"), ENGLISH_NOT_FOUND)

    def test_no_immediate_repetition(self):
        first = make_reply("test", "example", "en")
        second = make_reply("test", "example", "en")
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
