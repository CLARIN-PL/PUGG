import re
import urllib
from html.parser import HTMLParser

import requests


class WikipediaClient:
    wiki_content_api_address = (
        "https://pl.wikipedia.org/w/api.php?action=query&prop=revisions&rvslots=*&rvprop=content&"
        "formatversion=2&format=json&titles="
    )

    def __init__(self) -> None:
        self.wiki_text_cleaner = WikipediaTextCleaner()

    def retrieve_content(self, page_name: str) -> tuple[list[dict[str, int | str]], str]:
        page_content = requests.get(self.wiki_content_api_address + urllib.parse.quote(page_name))
        raw_text = page_content.json()["query"]["pages"][0]["revisions"][0]["slots"]["main"][
            "content"
        ]
        wiki_text = self.wiki_text_cleaner.clean_text(raw_text)
        wiki_links, plain_text = self._extract_links(wiki_text)
        return wiki_links, plain_text.rstrip()

    def _extract_links(self, wiki_text: str) -> tuple[list[dict[str, int | str]], str]:
        copy_wiki_text = wiki_text
        active = 0
        replace_link = ""
        word = ""
        url = ""
        wiki_links = []

        for idx in range(len(wiki_text)):
            if wiki_text[idx : idx + 2] == "[[":
                active = 1
            elif wiki_text[idx : idx + 2] == "]]" and active != 0:
                active = 0
                start_idx = copy_wiki_text.find("[[" + replace_link + "]]")
                end_idx = start_idx + len(word)
                copy_wiki_text = copy_wiki_text.replace("[[" + replace_link + "]]", word, 1)
                link_info: dict[str, str | int] = {
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                    "wiki_link": "https://pl.wikipedia.org/wiki/" + url,
                }
                wiki_links.append(link_info)

                replace_link = ""
                word = ""
                url = ""
            elif wiki_text[idx] == "|" and active == 1:
                active = 2
                replace_link += "|"
                word = ""
            elif active == 1 and wiki_text[idx] not in {"[", "]"}:
                replace_link += wiki_text[idx]
                word += wiki_text[idx]
                url += wiki_text[idx]
            elif active == 2:
                replace_link += wiki_text[idx]
                word += wiki_text[idx]
        return wiki_links, copy_wiki_text


class TagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.reset()
        self.fed: list[str] = []

    def handle_data(self, d: str) -> None:
        self.fed.append(d)

    def get_data(self) -> str:
        return "".join(self.fed)


class WikipediaTextCleaner:
    file_in_lang = "Plik"
    unneeded_paragraph_list = [
        "Uwagi",
        "Przypisy",
        "Bibliografia",
        "Linki zewnętrzne",
        "Zobacz też",
    ]

    def __init__(self) -> None:
        self.hyperlink_cleaner = re.compile(r"\[http.*?\]")
        self.ref_cleaner = re.compile(r"<ref.*?</ref>")
        self.gallery_cleaner = re.compile(r"(?s)<gallery.*?</gallery>")
        self.triple_quotes = re.compile(r"'''")
        self.double_quotes = re.compile(r"''")
        self.new_lines_cleaner = re.compile(r"(\n)\1{2,}")

    def clean_text(self, text: str) -> str:
        text = re.sub(self.hyperlink_cleaner, "", text)
        text = re.sub(self.ref_cleaner, "", text)
        text = re.sub(self.gallery_cleaner, "", text)
        text = text.replace("__TOC__", "")
        text = self._remove_brackets(text)
        text = self._remove_tables(text)
        text = self._remove_files(text)
        text = self._remove_unneeded_paragraphs(text)
        text = self._remove_tags(text)
        text = self._clean_quotes(text)
        text = re.sub(self.new_lines_cleaner, "\n\n", text)
        text = text.strip()
        return text

    def _clean_quotes(self, text: str) -> str:
        text = re.sub(self.triple_quotes, "", text)
        text = re.sub(self.double_quotes, '"', text)
        return text

    def _remove_tags(self, text: str) -> str:
        tag_parser = TagParser()
        tag_parser.feed(text)
        return tag_parser.get_data()

    def _remove_tables(self, text: str) -> str:
        result = ""
        counter = 0
        for idx in range(len(text)):
            if text[idx : idx + 2] == "{|":
                counter += 1
            elif text[idx - 1 : idx + 1] == "|}" and counter > 0:
                # as research showed, sometimes there are symbols |} without a preliminary table creation.
                # example:
                # https://pl.wikipedia.org/w/index.php?title=Ekstraklasa_w_pi%C5%82ce_no%C5%BCnej_(2018/2019)&action=edit&section=7
                counter -= 1
            elif counter == 0:
                result += text[idx]
        assert counter == 0
        return result

    def _remove_brackets(self, text: str) -> str:
        result = ""
        counter = 0
        for idx in range(len(text)):
            if text[idx : idx + 2] == "{{":
                counter += 1
            elif text[idx] == "{" and counter != 0:
                counter += 1
            elif text[idx] == "}" and counter != 0:
                counter -= 1
            elif counter == 0:
                result += text[idx]
        assert counter == 0
        return result

    def _remove_files(self, text: str) -> str:
        counter = 0
        result = ""
        for idx in range(len(text)):
            # sometimes they have a file named in English, not in a Polish language
            if (
                text[idx : (idx + len(self.file_in_lang) + 3)] == f"[[{self.file_in_lang}:"
                or text[idx : idx + 7] == "[[File:"
            ):
                counter += 1
            elif text[idx] == "[" and counter != 0:
                counter += 1
            elif text[idx] == "]" and counter != 0:
                counter -= 1
            elif counter == 0:
                result += text[idx]
        assert counter == 0
        return result

    def _remove_unneeded_paragraphs(self, text: str) -> str:
        for par_name in self.unneeded_paragraph_list:
            text = text.split("== " + par_name + " ==")[0]
        return text
