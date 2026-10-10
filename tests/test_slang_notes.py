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


if __name__ == "__main__":
    unittest.main()
