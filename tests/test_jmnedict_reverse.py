import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dictionary"))

from search import lookup
from replies import make_dictionary_replies


class TestJMnedictReverse(unittest.TestCase):

    def test_islay(self):
        result = lookup("Islay")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "jmnedict_reverse")
        self.assertIn("アイレー島", result["meaning"])

    def test_fagen(self):
        result = lookup("Fagen")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "jmnedict_reverse")
        self.assertIn("フェイゲン", result["meaning"])

    def test_feigen(self):
        result = lookup("Feigen")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "jmnedict_reverse")
        self.assertIn("フェイゲン", result["meaning"])

    def test_case_insensitive(self):
        result = lookup("islay")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "jmnedict_reverse")
        self.assertIn("アイレー島", result["meaning"])


    def test_islay_reply(self):
        messages = make_dictionary_replies(lookup("Islay"))
        self.assertEqual(len(messages), 1)
        self.assertIn("アイレー島", messages[0])
        self.assertIn("日本語", messages[0])

    def test_multiple_candidates(self):
        result = lookup("Yurina")
        self.assertEqual(result["source"], "jmnedict_reverse")
        self.assertGreater(result["total_candidates"], 3)
        self.assertEqual(len(result["candidates"]), 3)

        messages = make_dictionary_replies(result)
        self.assertEqual(len(messages), 1)
        self.assertIn("候補", messages[0])

    def test_existing_dictionary_priority(self):
        result = lookup("computer")
        self.assertIsNotNone(result)
        self.assertNotEqual(result.get("source"), "jmnedict_reverse")

    def test_unknown_english_name(self):
        result = lookup("NonexistentProperName987654321")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
