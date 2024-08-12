import unittest
from unittest.mock import patch

from gqqd.api.wikipedia_entity_linking import EntityLinkingClient
from tests.test_entity_linking_client_mock_data import mock_responses


class TestEntityLinkingClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = EntityLinkingClient()

        def mocked_get(url):
            query = url.split("=")[-1]
            mock_response = mock_responses.get(query, {"query": {"search": []}})
            return MockResponse(mock_response)

        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data

            def json(self):
                return self.json_data

        self.mock_get_patcher = patch(
            "gqqd.api.utils.entity_linking_utils.requests.get", side_effect=mocked_get
        )
        self.mock_get = self.mock_get_patcher.start()

    def tearDown(self):
        self.mock_get_patcher.stop()

    def test_extract_exact_entities(self):
        test_cases = [
            ("kim był główny bohater opowieści wigilijnej", {"Bohater"}),
            ("ile jest linii tramwajowych we wrocławiu", {"Linia", "Tramwaj", "Wrocław"}),
            ("kto jest zwierzchnikiem sił zbrojnych w polsce", {"Polska", "Siła"}),
            ("kto był pierwszym koronowanym królem polski", {"Król", "Polska"}),
            ("kogo uderzył piorun w dziadach", {"Piorun"}),
        ]

        for text, expected_links in test_cases:
            wiki_titles = self.client.extract_exact_entities(text)
            self.assertEqual(wiki_titles, expected_links)

    def test_extract_mentioned_named_entities(self) -> None:
        test_cases = [
            ("jakie zabytki znajdują się w warszawie", ["Warszawa"], {"Warszawa"}),
            ("kim był główny bohater opowieści wigilijnej", ["Bohater"], set()),
        ]

        for question, neighbourhood, expected_entities in test_cases:
            wiki_titles = self.client.extract_mentioned_named_entities(question, neighbourhood)
            self.assertEqual(wiki_titles, expected_entities)

        # the named entity must be in the neighbourhood to be extracted (it was done to avoid confusing people or
        # places, e.g. "Morawiecki")
        test_cases = [
            ("kim naprawdę był morawiecki", [], set()),
            ("kim naprawdę był morawiecki", ["Kornel Morawiecki"], {"Kornel Morawiecki"}),
            ("kim naprawdę był morawiecki", ["Mateusz Morawiecki"], {"Mateusz Morawiecki"}),
        ]

        for question, neighbourhood, expected_entities in test_cases:
            wiki_titles = self.client.extract_mentioned_named_entities(question, neighbourhood)
            self.assertEqual(wiki_titles, expected_entities)

    def test_extract_mentioned_entities(self) -> None:
        # here we extract one-or-more-word entities, which are presented in the question as a word, a phrase,
        # or a synonym
        test_cases = [
            # "Opowieść wigilijna" - is a phrase
            (
                "kim był główny bohater opowieści wigilijnej",
                [
                    "Charles Dickens",
                    "Opowieść wigilijna",
                    "Boże Narodzenie",
                    "Jakub Marley",
                    "Duch minionych świąt Bożego Narodzenia",
                    "Ebenezer Scrooge",
                ],
                {"Opowieść wigilijna"},
            ),
            # Tramwaje we Wrocławiu - is a phrase
            (
                "ile jest linii tramwajowych we wrocławiu",
                [
                    "tramwaj",
                    "Zajezdnia",
                    "Pętla (transport publiczny)",
                    "Berlin",
                    "koncesja",
                    "Tramwaje we Wrocławiu",
                ],
                {"Tramwaje we Wrocławiu", "Tramwaj"},
            ),
            # Siły Zbrojne Rzeczypospolitej Polskiej - is a phrase
            # Naczelny dowódca sił zbrojnych - is a synonim to "Zwierzchnik sił zbrojonych"
            (
                "kto jest zwierzchnikiem sił zbrojnych w polsce",
                [
                    "Wojsko Polskie",
                    "Siły i środki walki zbrojnej",
                    "Polska",
                    "walka (wojsko)",
                    "Siły zbrojne",
                    "siły zbrojne",
                    "państwo",
                    "głowa państwa",
                    "Rząd (prawo)",
                    "siły zbrojne",
                    "Siły Zbrojne Rzeczypospolitej Polskiej",
                    "Naczelny dowódca sił zbrojnych",
                ],
                {
                    "Siły Zbrojne Rzeczypospolitej Polskiej",
                    "Polska",
                    "Naczelny dowódca sił zbrojnych",
                },
            ),
            # "Król Polski" - is a phrase
            # "Władcy Polski" - is a synonym to "Król Polski"
            (
                "kto był pierwszym koronowanym królem polski",
                [
                    "łacina",
                    "Monarcha",
                    "Władcy Polski",
                    "Korona Królestwa Polskiego",
                    "Rzeczpospolita Obojga Narodów",
                    "967",
                    "17 czerwca",
                    "1025",
                    "Władcy Polski",
                    "Monarchia wczesnopiastowska",
                    "Król Polski",
                    "Bolesław I Chrobry",
                ],
                {"Król Polski", "Władcy Polski"},
            ),
            # unfortunately, no entities where found
            (
                "kogo uderzył piorun w dziadach",
                [
                    "Grodno",
                    "Wilno",
                    "Chirurgia",
                    "higiena",
                    "patomorfologia",
                    "Adam Mickiewicz",
                    "Dziady (dramat)",
                    "Drezno",
                    "Adam Mickiewicz",
                    "arcydzieło",
                    "August Bécu",
                    "Dziady część III",
                ],
                set(),
            ),
        ]

        for question, neighbourhood, expected_entities in test_cases:
            wiki_titles = self.client.extract_mentioned_entities(question, neighbourhood)
            self.assertEqual(wiki_titles, expected_entities)

    def test_get_associated_pages(self) -> None:
        # If the link, suggested by the search (search["wiki_links"]), is not the answer to the question,
        # it falls into the category of associated pages.
        test_cases = [
            (
                "kto jest zwierzchnikiem sił zbrojnych w polsce",
                ["Siły Zbrojne Rzeczypospolitej Polskiej", "Naczelny dowódca sił zbrojnych"],
                ["Siły Zbrojne Rzeczypospolitej Polskiej", "Naczelny dowódca sił zbrojnych"],
            ),
            (
                "kto był pierwszym koronowanym królem polski",
                ["Król Polski", "Bolesław I Chrobry"],
                ["Król Polski"],
            ),
            # Sometimes it can provide additional entities, which were not extracted by the previous methods::
            (
                "kogo uderzył piorun w dziadach",
                ["August Bécu", "Dziady część III"],
                ["Dziady część III"],
            ),
        ]

        for question, wiki_pages, expected_pages in test_cases:
            result = self.client.get_associated_pages(question, wiki_pages)
            self.assertEqual(result, expected_pages)
