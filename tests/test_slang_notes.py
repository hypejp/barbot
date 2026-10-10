import unittest

from search import lookup
from replies import make_dictionary_replies


class TestSlangNotes(unittest.TestCase):

    def test_hype_lookup(self):
        result = lookup("hype")
        self.assertIsNotNone(result)
        self.assertEqual(result["meaning"], "誇大宣伝")

    def test_hype_slang_note(self):
        messages = make_dictionary_replies(lookup("hype"))
        self.assertEqual(len(messages), 2)
        self.assertIn("誇大宣伝", messages[0])
        self.assertIn("盛り上がり", messages[1])
        self.assertIn("期待をあおる", messages[1])

    def test_hype_uppercase(self):
        messages = make_dictionary_replies(lookup("HYPE"))
        self.assertEqual(len(messages), 2)
        self.assertIn("熱狂", messages[1])

    def test_no_slang_note_for_music(self):
        messages = make_dictionary_replies(lookup("music"))
        self.assertEqual(len(messages), 1)



class TestTranslationDeduplication(unittest.TestCase):

    def test_katakana_long_vowel_variants(self):
        from replies import unique_translations

        translations = [
            "コンピュータ",
            "コンピューター",
            "電子計算機",
        ]
        self.assertEqual(
            unique_translations(translations),
            ["コンピュータ", "電子計算機"],
        )

    def test_distinct_translations_are_preserved(self):
        from replies import unique_translations

        self.assertEqual(
            unique_translations(["音楽", "ミュージック"]),
            ["音楽", "ミュージック"],
        )

    def test_computer_reply(self):
        messages = make_dictionary_replies(lookup("computer"))
        self.assertEqual(len(messages), 1)
        self.assertIn("コンピュータ", messages[0])
        self.assertIn("電子計算機", messages[0])
        self.assertNotIn("コンピューター", messages[0])



class TestMusicTranslation(unittest.TestCase):

    def test_music_reply(self):
        messages = make_dictionary_replies(lookup("music"))

        self.assertEqual(len(messages), 1)
        self.assertIn("『音楽』", messages[0])
        self.assertIn("『楽譜』", messages[0])
        self.assertNotIn("『ミュージック』", messages[0])

    def test_music_translation_exclusion(self):
        from overrides import TRANSLATION_EXCLUSIONS

        self.assertIn("ミュージック", TRANSLATION_EXCLUSIONS["music"])


if __name__ == "__main__":
    unittest.main()
