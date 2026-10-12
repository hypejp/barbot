import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dictionary"))

from search import lookup
from jmnedict import lookup as lookup_name
from replies import make_dictionary_replies


class TestJMnedict(unittest.TestCase):

    def test_person_name(self):
        result = lookup("徳川家康")
        self.assertEqual(result["source"], "jmnedict")
        self.assertIn("Tokugawa Ieyasu", result["meaning"])
        self.assertIn("full name of a particular person", result["name_types"])

    def test_station_name(self):
        result = lookup("東京駅")
        self.assertEqual(result["source"], "jmnedict")
        self.assertEqual(result["meaning"], "Tokyo Station")

    def test_existing_jmdict_priority(self):
        result = lookup("大阪")
        self.assertNotEqual(result.get("source"), "jmnedict")
        self.assertIn("Osaka", result["meaning"])

    def test_multiple_name_types(self):
        result = lookup_name("大阪")
        self.assertIn("place name", result["name_types"])
        self.assertIn("family or surname", result["name_types"])

    def test_unknown_name(self):
        self.assertIsNone(lookup_name("存在しない固有名詞123"))

    def test_person_reply(self):
        messages = make_dictionary_replies(lookup("徳川家康"))
        self.assertEqual(len(messages), 1)
        self.assertIn("1543-1616", messages[0])
        self.assertIn("shogun from 1603 to 1605", messages[0])
        self.assertIn("Tokugawa Ieyasu", messages[0])

    def test_station_reply(self):
        messages = make_dictionary_replies(lookup("東京駅"))
        self.assertIn("railway station", messages[0])
        self.assertIn("Tokyo Station", messages[0])


    def test_multiple_surname_readings(self):
        messages = make_dictionary_replies(lookup("東海林"))
        self.assertEqual(len(messages), 1)
        self.assertIn("Japanese surname", messages[0])
        self.assertIn("Possible readings include", messages[0])
        self.assertIn("しょうじ (Shouji)", messages[0])
        self.assertIn("とうかいりん (Tōkairin)", messages[0])


    def test_islay_alias(self):
        result = lookup("アイラ島")
        self.assertEqual(result["source"], "jmnedict")
        self.assertIn("Islay", result["meaning"])
        self.assertTrue(result["word"].startswith("アイラ島("))

    def test_islay_original_spelling(self):
        result = lookup("アイレー島")
        self.assertEqual(result["source"], "jmnedict")
        self.assertIn("Islay", result["meaning"])
        self.assertTrue(result["word"].startswith("アイレー島("))

    def test_ira_name_unchanged(self):
        result = lookup("アイラ")
        self.assertEqual(result["source"], "jmnedict")
        self.assertEqual(result["meaning"], "Ira")


if __name__ == "__main__":
    unittest.main()
