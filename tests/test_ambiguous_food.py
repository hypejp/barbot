import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dictionary"))

from search import lookup
from replies import make_dictionary_replies


class TestAmbiguousFood(unittest.TestCase):
    def reply(self, word):
        result = lookup(word)
        self.assertIsNotNone(result)
        return "\n".join(make_dictionary_replies(result))

    def test_zenzai(self):
        reply = self.reply("ぜんざい")
        self.assertIn("zenzai (Japanese sweet red bean soup", reply)
        self.assertNotIn("well done!", reply)

    def test_monaka(self):
        reply = self.reply("もなか")
        self.assertIn("monaka (Japanese wafer confection", reply)

    def test_saichu(self):
        for word in ("最中", "さいちゅう"):
            with self.subTest(word=word):
                reply = self.reply(word)
                self.assertIn("(in) the middle of", reply)
                self.assertNotIn("Japanese wafer confection", reply)

    def test_akashiyaki(self):
        reply = self.reply("明石焼き")
        self.assertIn("akashiyaki (soft egg-rich octopus dumplings", reply)
        self.assertNotIn("pottery", reply)

    def test_champon(self):
        reply = self.reply("ちゃんぽん")
        self.assertIn("champon (Nagasaki-style noodle soup", reply)

    def test_non_food(self):
        reply = self.reply("自転車")
        self.assertIn("bicycle", reply)
        self.assertNotIn("Food:", reply)


if __name__ == "__main__":
    unittest.main()
