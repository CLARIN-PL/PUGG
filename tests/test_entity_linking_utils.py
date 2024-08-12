import unittest
from unittest.mock import patch

from gqqd.api.utils.entity_linking_utils import (
    capitalize_every_word,
    get_top_n_wiki_search_result,
    search_mentioned,
    two_texts_similarity,
)


class TestCode(unittest.TestCase):
    def test_capitalize_every_word(self):
        self.assertEqual(
            capitalize_every_word("kim był główny bohater opowieści wigilijnej"),
            "Kim Był Główny Bohater Opowieści Wigilijnej",
        )
        self.assertEqual(
            capitalize_every_word("ile jest linii tramwajowych we wrocławiu"),
            "Ile Jest Linii Tramwajowych We Wrocławiu",
        )
        self.assertEqual(capitalize_every_word(""), "")

    @patch("gqqd.api.utils.entity_linking_utils.requests.get")
    def test_get_wiki_search_result(self, mock_get):
        # Mock the API response
        mock_response1 = {
            "query": {
                "search": [
                    {"title": "Bohater", "pageid": 123},
                    {"title": "Bohater bajroniczny", "pageid": 1723},
                    {"title": "Bohater niezależny", "pageid": 1243},
                ]
            }
        }

        mock_response2 = {
            "query": {
                "search": [
                    {"title": "Rynek Główny w Krakowie", "pageid": 1123},
                    {"title": "Siedem grzechów głównych", "pageid": 1234},
                    {"title": "Główny Urząd Statystyczny", "pageid": 12323},
                ]
            }
        }

        mock_get.return_value.json.side_effect = [mock_response1, mock_response2]

        # Test for "bohater" query
        wiki_titles = get_top_n_wiki_search_result("bohater")
        expected_result = ["Bohater", "Bohater bajroniczny", "Bohater niezależny"]
        self.assertEqual(wiki_titles, expected_result)

        # Test for "główny" query
        wiki_titles = get_top_n_wiki_search_result("główny")
        expected_result = [
            "Rynek Główny w Krakowie",
            "Siedem grzechów głównych",
            "Główny Urząd Statystyczny",
        ]
        self.assertEqual(wiki_titles, expected_result)

    def test_two_words_similarity(self):
        # Kim był główny bohater opowieści wigilijnej?
        self.assertEqual(
            two_texts_similarity("główny", "rynek główny w krakowie"),
            0.0 + len("głowny") / len("rynek główny w krakowie"),
        )
        self.assertEqual(
            two_texts_similarity("wigilijny", "wigilijny barszcz z uszkami"),
            len("wigilijny") / len("wigilijny barszcz z uszkami") * 2,
        )
        self.assertEqual(
            two_texts_similarity("opowieść", "opowieść wigilijna"),
            len("opowieść") / len("opowieść wigilijna") * 2,
        )
        self.assertEqual(two_texts_similarity("bohater", "bohater"), 1.0 + 1.0)

        # ile jest linii tramwajowych we wrocławiu?
        self.assertEqual(
            two_texts_similarity("linia", "linia m2 metra w warszawie"),
            len("linia") / len("linia m2 metra w warszawie") * 2,
        )
        self.assertEqual(two_texts_similarity("tramwajowy", "tramwaj"), 1.0 + 1.0)
        self.assertEqual(two_texts_similarity("wrocławiu", "wrocław"), 1.0 + 1.0)

    @patch("gqqd.api.utils.entity_linking_utils.requests.get")
    def test_search_mentioned(self, mock_get):
        mock_response = {
            "query": {
                "search": [
                    {"title": "Opowieść wigilijna", "pageid": 456},
                    {"title": "Opowieść wigilijna (film 2009)", "pageid": 876},
                    {"title": "Opowieść wigilijna Myszki Miki", "pageid": 451},
                ]
            }
        }
        mock_get.return_value.json.return_value = mock_response
        result = search_mentioned(
            "Opowieść wigilijna",
            [
                "Charles Dickens",
                "Opowieść wigilijna",
                "Boże Narodzenie",
                "Jakub Marley",
                "Duch minionych świąt Bożego Narodzenia",
                "Ebenezer Scrooge",
            ],
        )
        mock_get.assert_called_with(
            "https://pl.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch=Opowieść wigilijna"
        )

        mock_response = {
            "query": {
                "search": [
                    {"title": "Linia", "pageid": 1213},
                    {"title": "Linia M2 metra w Warszawie", "pageid": 1613},
                    {"title": "Linia Curzona", "pageid": 1289},
                ]
            }
        }
        self.assertEqual(result, "Opowieść wigilijna")
        result = search_mentioned(
            "linia",
            [
                "tramwaj",
                "Zajezdnia",
                "Pętla (transport publiczny)",
                "Berlin",
                "koncesja",
                "Tramwaje we Wrocławiu",
            ],
        )
        self.assertEqual(result, None)
        mock_get.assert_called_with(
            "https://pl.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch=linia"
        )
