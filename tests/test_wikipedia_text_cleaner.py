import unittest

from gqqd.api.wikipedia_content_client import WikipediaTextCleaner


class TestWikipediaTextCleaner(unittest.TestCase):
    def setUp(self) -> None:
        self.cleaner = WikipediaTextCleaner()

    def test_cleaning_quotes(self) -> None:
        quotes_cleaner = self.cleaner._clean_quotes

        test_cases = [
            ("'''Some text''' in triple quotes.", "Some text in triple quotes."),
            ("''Some text'' in double quotes", '"Some text" in double quotes'),
        ]

        for test_text, expected_output in test_cases:
            self.assertEqual(quotes_cleaner(test_text), expected_output)

    def test_table_cleaning(self) -> None:
        table_remover = self.cleaner._remove_tables
        test_cases = [
            (
                "{|some text|}Brackets at the beginning of the text.",
                "Brackets at the beginning of the text.",
            ),
            (
                "Brackets at the end of the text.{|some text|}",
                "Brackets at the end of the text.",
            ),
            (
                "Brackets with a single symbol after{|some text|}.",
                "Brackets with a single symbol after.",
            ),
            (
                " {|some text|}Brackets with a single symbol before.",
                " Brackets with a single symbol before.",
            ),
            (
                "Brackets in the middle{|some text|} of the text.",
                "Brackets in the middle of the text.",
            ),
            (
                "Several brackets{|some text|} in the middle{|some text|} of the text.",
                "Several brackets in the middle of the text.",
            ),
            (
                "Brackets inside the brackets{|some text{|some text|}|}.",
                "Brackets inside the brackets.",
            ),
        ]

        for test_text, expected_output in test_cases:
            self.assertEqual(table_remover(test_text), expected_output)

    def test_tags_remove(self) -> None:
        tags_remover = self.cleaner._remove_tags

        text_with_tags = (
            "<p>This is some <b>sample</b> text<br> with <i>different</i> <u>tags</u>.</p>"
        )
        expected_output_without_tags = "This is some sample text with different tags."
        self.assertEqual(tags_remover(text_with_tags), expected_output_without_tags)

        text_without_tags = "2<3 This is some text without tags. 3>2"
        self.assertEqual(tags_remover(text_without_tags), text_without_tags)

    def test_brackets_remove(self) -> None:
        brackets_remover = self.cleaner._remove_brackets
        test_cases = [
            (
                "{{some text}}Brackets at the beginning of the text.",
                "Brackets at the beginning of the text.",
            ),
            (
                "Brackets at the end of the text.{{some text}}",
                "Brackets at the end of the text.",
            ),
            (
                "Brackets with a single symbol after{{some text}}.",
                "Brackets with a single symbol after.",
            ),
            (
                " {{some text}}Brackets with a single symbol before.",
                " Brackets with a single symbol before.",
            ),
            (
                "Brackets in the middle{{some text}} of the text.",
                "Brackets in the middle of the text.",
            ),
            (
                "Several brackets{{some text}} in the middle{{some text}} of the text.",
                "Several brackets in the middle of the text.",
            ),
            (
                "Brackets inside the brackets{{some text{{some text}}}}.",
                "Brackets inside the brackets.",
            ),
        ]

        for test_text, expected_output in test_cases:
            self.assertEqual(brackets_remover(test_text), expected_output)

    def test_files_remove(self) -> None:
        file_remover = self.cleaner._remove_files
        file_in_lang = self.cleaner.file_in_lang
        test_cases = [
            (
                "[[" + file_in_lang + ": File.jpg]]File at the beginning of the text.",
                "File at the beginning of the text.",
            ),
            (
                "File at the end of the text.[[" + file_in_lang + ": File.jpg]]",
                "File at the end of the text.",
            ),
            (
                "File with a single symbol after[[" + file_in_lang + ": File.jpg]].",
                "File with a single symbol after.",
            ),
            (
                " [[" + file_in_lang + ": File.jpg]]File with a single symbol before.",
                " File with a single symbol before.",
            ),
            (
                "File in the middle [[" + file_in_lang + ": File.jpg]]of the text.",
                "File in the middle of the text.",
            ),
            (
                "Several files[["
                + file_in_lang
                + ": File.jpg]] in the[["
                + file_in_lang
                + ": File.jpg]] text.",
                "Several files in the text.",
            ),
            (
                "File with a link inside[[" + file_in_lang + ": File[[Link | File]].jpg]].",
                "File with a link inside.",
            ),
            (
                "A [[Link | link]] that should not be removed.",
                "A [[Link | link]] that should not be removed.",
            ),
        ]

        for test_text, expected_output in test_cases:
            self.assertEqual(file_remover(test_text), expected_output)

    def test_unneeded_paragraphs_remove(self) -> None:
        paragraphs_remover = self.cleaner._remove_unneeded_paragraphs
        test_text = """
        This is some sample text.
        == Przypisy ==
        This is some unneeded text"
        """
        expected_output = """
        This is some sample text.
        """
        self.assertEqual(paragraphs_remover(test_text), expected_output)

    def test_text_cleaning_all(self) -> None:
        test_text = (
            """
        <p>This is some <b>sample</b> text with <i>tags</i> and <u>formatting</u>.</p>
        {{Bracketed text}}
        [["""
            + self.cleaner.file_in_lang
            + """:File.jpg]]
        == Uwagi ==
        This is some unneeded paragraph text.
        <gallery> Some files </gallery>
        <ref> Some links </ref>
        __TOC__
        """
        )
        expected_output = "This is some sample text with tags and formatting."
        self.assertEqual(expected_output, self.cleaner.clean_text(test_text))
