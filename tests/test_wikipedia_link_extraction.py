import unittest

from gqqd.api.wikipedia_content_client import WikipediaClient


class TestWikipediaClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = WikipediaClient()

    def test_extract_links(self) -> None:
        test_cases = [
            (
                "This is a [[link]] to a Wikipedia page.",
                [
                    {
                        "start_idx": 10,
                        "end_idx": 14,
                        "wiki_link": "https://pl.wikipedia.org/wiki/link",
                    }
                ],
                "This is a link to a Wikipedia page.",
            ),
            (
                "This is a [[link|displayed text]] to a Wikipedia page.",
                [
                    {
                        "start_idx": 10,
                        "end_idx": 24,
                        "wiki_link": "https://pl.wikipedia.org/wiki/link",
                    }
                ],
                "This is a displayed text to a Wikipedia page.",
            ),
            (
                "This is a [[link]] to a Wikipedia page. And this is another [[link]].",
                [
                    {
                        "start_idx": 10,
                        "end_idx": 14,
                        "wiki_link": "https://pl.wikipedia.org/wiki/link",
                    },
                    {
                        "start_idx": 56,
                        "end_idx": 60,
                        "wiki_link": "https://pl.wikipedia.org/wiki/link",
                    },
                ],
                "This is a link to a Wikipedia page. And this is another link.",
            ),
            (
                "[[Link]] at the beginning of the text.",
                [
                    {
                        "start_idx": 0,
                        "end_idx": 4,
                        "wiki_link": "https://pl.wikipedia.org/wiki/Link",
                    }
                ],
                "Link at the beginning of the text.",
            ),
            (
                "Link at the end of the text [[link]]",
                [
                    {
                        "start_idx": 28,
                        "end_idx": 32,
                        "wiki_link": "https://pl.wikipedia.org/wiki/link",
                    }
                ],
                "Link at the end of the text link",
            ),
        ]

        for text, expected_wiki_links, expected_plain_text in test_cases:
            wiki_links, plain_text = self.client._extract_links(text)
            self.assertEqual(wiki_links, expected_wiki_links)
            self.assertEqual(plain_text, expected_plain_text)
