import unittest

import spacy
from spacy.language import Language

from gqqd.api.utils.association_lookup_utils import (
    _extend_word_endings,
    _lemmatize_repeatedly,
    _lemmatize_tokens,
    create_extended_word_set,
)


class TestLemmatizer(unittest.TestCase):
    def setUp(self):
        self.nlp = spacy.load("pl_core_news_sm")

    def test_lemmatize_tokens(self):
        # an example with correct lemmatization
        text = "opowieść wigilijna"
        expected = {"opowieść", "wigilijny"}
        result = _lemmatize_tokens(text, self.nlp)
        self.assertEqual(result, expected)

        # an example in which a repeated lemmatization is needed
        text = "dziady część III"
        expected = {"dziada", "część", "III"}
        result = _lemmatize_tokens(text, self.nlp)
        self.assertEqual(result, expected)

        # an example in which extending word endings is needed
        text = "Freddie Mercury"
        expected = {"Freddie", "Mercura"}
        result = _lemmatize_tokens(text, self.nlp)
        self.assertEqual(result, expected)

    def test_lemmatize_repeatedly(self):
        word_set = {"dziada", "część", "III"}
        expected = {"dziad", "część", "III"}
        result = _lemmatize_repeatedly(word_set, self.nlp)
        self.assertEqual(result, expected)

    def test_extend_word_endings(self):
        text_set = {"Freddie", "Mercura"}
        expected = {"Freddie", "Mercura", "Freddi", "Mercur", "Fredd", "Mercu"}
        result = _extend_word_endings(text_set)
        self.assertEqual(result, expected)

    def test_create_extended_word_set(self):
        text = "kogo uderzył piorun w dziadach"
        expected = {"dziad", "dzia", "piorun", "pioru", "pior", "uderzyć", "uderzy", "uderz"}
        result = create_extended_word_set(text, self.nlp)
        self.assertEqual(result, expected)
