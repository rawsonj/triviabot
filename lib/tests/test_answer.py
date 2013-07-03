from unittest import TestCase

from lib.answer import Answer


class TestAnswer(TestCase):

    def test_masking(self):
        answer = Answer("test")
        self.assertEqual(answer.current_clue(), "****")

    def test_masking_spaces(self):
        answer = Answer("test spaces")
        self.assertEqual(answer.current_clue(), "**** ******")
