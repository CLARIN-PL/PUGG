import unittest
from functools import cache

import pandas as pd
import pytest
from tqdm import tqdm

from gqqd.data.loaders import load_wiki_content_df
from gqqd.defaults import ANNOTATED_PATH, OUTPUT_PATH, WIKI_RESULTS

skip_context_not_exists = pytest.mark.skipif(
    not (WIKI_RESULTS / "db_fixed.json").exists(), reason="wiki context not exists"
)
skip_qa_for_annotation_not_exists = pytest.mark.skipif(
    not (OUTPUT_PATH / "qa_for_annotation_testing.json").exists(),
    reason="qa_for_annotation not exists",
)
skip_auto_annotated_not_exists = pytest.mark.skipif(
    not (ANNOTATED_PATH / "gpt_auto_annotated_iteration_0.json").exists(),
    reason="gpt_auto_annotated_iteration_0.json not exists",
)


@skip_context_not_exists
@skip_qa_for_annotation_not_exists
@skip_auto_annotated_not_exists
class TestLinksAgreement(unittest.TestCase):
    def setUp(self) -> None:
        self.wiki_content_df = load_wiki_content_df()

    def test_agreement_for_annotation(self):
        qa_for_annotation_df = pd.read_json(OUTPUT_PATH / "qa_for_annotation.json")
        for x in tqdm(qa_for_annotation_df.itertuples(), total=len(qa_for_annotation_df)):
            for passage in x.passages:
                original_links = self._get_original_links(passage["wiki_page"])

                for link in passage["links"]:
                    org_link_rows = original_links[original_links.wiki_link == link["wiki_link"]]
                    link_text = passage["text"][link["start_idx"] : link["end_idx"]]
                    assert (
                        org_link_rows["text"].eq(link_text).any().tolist()
                    ), f"{link_text} is not in \n{org_link_rows}"

    def test_agreement_auto_annotated(self):
        auto_annotated_df = pd.read_json(ANNOTATED_PATH / "gpt_auto_annotated_iteration_0.json")
        for x in tqdm(auto_annotated_df.itertuples(), total=len(auto_annotated_df)):
            passage = x.passage
            original_links = self._get_original_links(passage["wiki_page"])

            for link in passage["links"]:
                org_link_rows = original_links[original_links.wiki_link == link["wiki_link"]]
                link_text = passage["text"][link["start_idx"] : link["end_idx"]]
                assert (
                    org_link_rows["text"].eq(link_text).any().tolist()
                ), f"{link_text} is not in \n{org_link_rows}"

    @cache
    def _get_original_links(self, page: str) -> pd.DataFrame:
        [row] = self.wiki_content_df[self.wiki_content_df.page == page].iloc
        original_page = dict(row)
        original_links = pd.DataFrame(original_page["wiki_links"])
        original_links["text"] = [
            original_page["plain_text"][x.start_idx : x.end_idx]
            for x in original_links.itertuples()
        ]
        return original_links
