import unittest

from gqqd.pipeline.passage_retrieval import PassageConstructor


class TestPassageConstructorFullCoverage(unittest.TestCase):
    def setUp(self) -> None:
        self.constructor = PassageConstructor(10, 5)

    def test_text_full_coverage_not_needed(self):
        text = " ".join(str(x) for x in range(50))
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0 1 2 3 4 5 6 7 8 9", split_text[0])
        self.assertEqual("40 41 42 43 44 45 46 47 48 49", split_text[-1])
        self.assertEqual(9, len(split_text))
        self.assertEqual(9, len(split_idx))
        self.assertEqual(text[split_idx[0][0]], split_text[0][0])
        self.assertEqual(text[split_idx[0][0] + 4], split_text[0][4])
        self.assertEqual(text[split_idx[0][1] - 1], split_text[0][-1])
        self.assertEqual(text[split_idx[3][0]], split_text[3][0])
        self.assertEqual(text[split_idx[3][0] + 4], split_text[3][4])
        self.assertEqual(text[split_idx[3][1] - 1], split_text[3][-1])

    def test_text_full_coverage_needed(self):
        text = " ".join(str(x) for x in range(57))
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0 1 2 3 4 5 6 7 8 9", split_text[0])
        self.assertEqual("47 48 49 50 51 52 53 54 55 56", split_text[-1])
        self.assertEqual(11, len(split_text))
        self.assertEqual(11, len(split_idx))
        self.assertEqual(text[split_idx[0][0]], split_text[0][0])
        self.assertEqual(text[split_idx[0][0] + 4], split_text[0][4])
        self.assertEqual(text[split_idx[0][1] - 1], split_text[0][-1])
        self.assertEqual(text[split_idx[-1][0]], split_text[-1][0])
        self.assertEqual(text[split_idx[-1][0] + 4], split_text[-1][4])
        self.assertEqual(text[split_idx[-1][1] - 1], split_text[-1][-1])
        self.assertEqual(text[split_idx[-1][0] : split_idx[-1][1]], split_text[-1])

    def test_short_text(self):
        text = " ".join(str(x) for x in range(3))
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0 1 2", split_text[0])
        self.assertEqual(1, len(split_text))

    def test_empty_text(self):
        text = ""
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual([], split_text)

    def test_equal_to_window_text(self):
        text = " ".join(str(x) for x in range(10))
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0 1 2 3 4 5 6 7 8 9", split_text[0])
        self.assertEqual(1, len(split_text))

    def test_wiki_links_correctness(self):
        text = " ".join(str(x) for x in range(50))
        wiki_links = [
            {
                "start_idx": text.index("3"),
                "end_idx": text.index("3") + 1,
                "wiki_link": "https://pl.wikipedia.org/wiki/3",
            },
            {
                "start_idx": text.index("10"),
                "end_idx": text.index("10") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/10",
            },
            {
                "start_idx": text.index("13"),
                "end_idx": text.index("13") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/13",
            },
            {
                "start_idx": text.index("49"),
                "end_idx": text.index("49") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/49",
            },
        ]
        passages, passages_links = self.constructor.construct(text, wiki_links)

        self.assertEqual(passages_links[0][0].keys(), wiki_links[0].keys())

        for passage, links in zip(passages, passages_links):
            for link_dict in links:
                self.assertEqual(
                    "https://pl.wikipedia.org/wiki/"
                    + passage[link_dict["start_idx"] : link_dict["end_idx"]],
                    link_dict["wiki_link"],
                )

    def test_wiki_links_correctness_full_coverage(self):
        text = " ".join(str(x) for x in range(5))
        wiki_links = [
            {
                "start_idx": text.index("0"),
                "end_idx": text.index("0") + 1,
                "wiki_link": "https://pl.wikipedia.org/wiki/0",
            },
            {
                "start_idx": text.index("3"),
                "end_idx": text.index("3") + 1,
                "wiki_link": "https://pl.wikipedia.org/wiki/3",
            },
        ]
        passages, passages_links = self.constructor.construct(text, wiki_links)

        for passage, links in zip(passages, passages_links):
            for link_dict in links:
                self.assertEqual(
                    passage[link_dict["start_idx"] : link_dict["end_idx"]],
                    text[link_dict["start_idx"] : link_dict["end_idx"]],
                )

    def test_wiki_links_correctness_full_coverage_longer(self):
        text = " ".join(str(x) for x in range(12))
        wiki_links = [
            {
                "start_idx": text.index("1"),
                "end_idx": text.index("1") + 1,
                "wiki_link": "https://pl.wikipedia.org/wiki/1",
            },
            {
                "start_idx": text.index("11"),
                "end_idx": text.index("11") + 1,
                "wiki_link": "https://pl.wikipedia.org/wiki/1",
            },
        ]
        passages, passages_links = self.constructor.construct(text, wiki_links)

        self.assertEqual(
            passages[0][passages_links[0][0]["start_idx"] : passages_links[0][0]["end_idx"]],
            text[wiki_links[0]["start_idx"] : wiki_links[0]["end_idx"]],
        )
        self.assertEqual(
            passages[1][passages_links[1][0]["start_idx"] : passages_links[1][0]["end_idx"]],
            text[wiki_links[1]["start_idx"] : wiki_links[1]["end_idx"]],
        )

    def test_error_when_not_stripped(self):
        text = " ".join(str(x) for x in range(10)) + " "
        with self.assertRaises(ValueError):
            self.constructor.construct(text, [])

        text = " "
        with self.assertRaises(ValueError):
            self.constructor.construct(text, [])

    def test_sequence_deconstruct_reconstruct(self):
        text = "a r t t\tks\nks\t p"
        split_text, whitespaces = self.constructor._deconstruct_sequence(text)
        result = self.constructor._reconstruct_sequence(split_text, whitespaces)
        self.assertEqual(result, text)

    def test_passage_correct_whitespaces(self):
        text = "0\t1 2\n3\t\t\n\n\n4 5 6 7 8 9 10\t\t11 12 13 14 15 16 17 18 19  20\n\n21\t\t22"
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0\t1 2\n3\t\t\n\n\n4 5 6 7 8 9", split_text[0])
        self.assertEqual(text[split_idx[0][0]], split_text[0][0])
        self.assertEqual(text[split_idx[0][0] + 4], split_text[0][4])
        self.assertEqual(text[split_idx[0][1] - 1], split_text[0][-1])

        self.assertEqual(text[split_idx[1][0]], split_text[1][0])
        self.assertEqual(text[split_idx[1][1] - 1], split_text[1][-1])
        self.assertEqual(text[split_idx[1][0] : split_idx[1][1]], split_text[1])

        self.assertEqual(text[split_idx[-1][0]], split_text[-1][0])
        self.assertEqual(text[split_idx[-1][0] + 4], split_text[-1][4])
        self.assertEqual(text[split_idx[-1][1] - 1], split_text[-1][-1])
        self.assertEqual(text[split_idx[-1][0] : split_idx[-1][1]], split_text[-1])

    def test_wiki_links_correct_whitespaces(self):
        text = "0\t1 2\n3\t\t\n\n\n4 5 6 7 8 9 10\t\t11 12 13 14 15 16 17 18 19  20\n\n21\t\t22"
        wiki_links = [
            {
                "start_idx": text.index("10"),
                "end_idx": text.index("10") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/10",
            },
            {
                "start_idx": text.index("13"),
                "end_idx": text.index("13") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/13",
            },
            {
                "start_idx": text.index("21"),
                "end_idx": text.index("21") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/21",
            },
            {
                "start_idx": text.index("22"),
                "end_idx": text.index("22") + 2,
                "wiki_link": "https://pl.wikipedia.org/wiki/22",
            },
        ]
        passages, passages_links = self.constructor.construct(text, wiki_links)

        self.assertEqual(passages_links[1][0].keys(), wiki_links[0].keys())

        for passage, links in zip(passages, passages_links):
            for link_dict in links:
                self.assertEqual(
                    "https://pl.wikipedia.org/wiki/"
                    + passage[link_dict["start_idx"] : link_dict["end_idx"]],
                    link_dict["wiki_link"],
                )

    def test_wiki_link_not_exist_on_edge(self):
        text = " ".join(str(x) for x in range(20))
        wiki_links = [
            {
                "start_idx": text.index("9 10"),
                "end_idx": text.index("9 10") + len("9 10"),
                "wiki_link": "https://pl.wikipedia.org/wiki/1",
            }
        ]

        passages, passages_links = self.constructor.construct(text, wiki_links)
        assert len(passages_links[0]) == 0
        assert len(passages_links[1]) == 1
        assert len(passages_links[2]) == 0


class TestPassageConstructorNotFullCoverage(unittest.TestCase):
    def setUp(self) -> None:
        self.constructor = PassageConstructor(10, 5, ensure_full_coverage=False)

    def test_not_full_coverage(self):
        text = " ".join(str(x) for x in range(13))
        split_text, split_idx = self.constructor.split_on_window(text)
        self.assertEqual("0 1 2 3 4 5 6 7 8 9", split_text[0])
        self.assertEqual(1, len(split_text))
