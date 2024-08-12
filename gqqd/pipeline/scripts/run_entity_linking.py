import traceback
from dataclasses import dataclass
from itertools import chain
from typing import Collection, Dict, Optional, Sequence

import pandas as pd
import srsly
import typer
from mpire import WorkerPool
from tinydb import TinyDB

from gqqd.api.wikipedia_entity_linking import EntityLinkingClient
from gqqd.data.loaders import get_search_results_df
from gqqd.defaults import ENTITY_LINKING_INPUT, ENTITY_LINKING_PROCESSED, WIKI_RESULTS
from gqqd.utils.utils import get_current_time_str, insert_to_table_and_clean_buffer

BUFFER_CHUNK_SIZE = 50
PREFIX = "https://pl.wikipedia.org/wiki/"


@dataclass(slots=True)
class EntityLinkingResult:
    question: str
    direct_pages: list[str]
    associated_pages: list[str]


def extract_linked_entities(pages: list[str], page_links: dict[str, list[str]]) -> list[str]:
    # Later we will use the list of entities that are related to the query. That list (or as I call it the
    # "neighborhood") is constructed from wiki-pages provided by the search engine and from the first n links in
    # each of the provided Wikipedia pages).
    one_hop_neighborhood = list(
        chain.from_iterable([page_links.get(page, [])[:5] for page in pages])
    )
    return one_hop_neighborhood + pages


def process_search_results(search_results_df: pd.DataFrame) -> pd.DataFrame:
    wiki_db = TinyDB(WIKI_RESULTS / "db.json", indent=4, ensure_ascii=False)
    results_table = wiki_db.table("results")
    page_links = dict()
    for r in results_table:
        links = r["wiki_links"]
        links_without_prefix = []
        prefix_len = len(PREFIX)
        for link in links:
            assert link["wiki_link"].startswith(PREFIX)
            links_without_prefix.append(link["wiki_link"][prefix_len:])
        page_links[r["page"]] = links_without_prefix
    search_results_df = search_results_df[search_results_df["wiki_pages"].apply(len) > 0]
    search_results_df["linked_entities"] = search_results_df["wiki_pages"].apply(
        lambda pages: extract_linked_entities(pages, page_links)
    )
    return search_results_df


def process_question(
    el_client: EntityLinkingClient,
    question: str,
    neighbours: list[str],
    wiki_pages: list[str],
) -> Optional[Dict[str, Sequence[Collection[str]]]]:
    try:
        direct_pages, associated_pages = el_client.get_results(question, neighbours, wiki_pages)
        result = {
            "question": question,
            "direct_pages": list(direct_pages),
            "associated_pages": associated_pages,
            "time": get_current_time_str(),
        }
    except Exception:
        traceback.print_exc()
        print(f"{get_current_time_str()}: Skipping page: '{question}' due to the exception. ")
        return None
    return result


def main(n_jobs: int = typer.Option(default=50), iteration: int = typer.Option(default=0)) -> None:
    ENTITY_LINKING_PROCESSED.mkdir(exist_ok=True)
    db = TinyDB(
        ENTITY_LINKING_PROCESSED / f"{iteration}/entity_linking_results.json",
        indent=4,
        ensure_ascii=False,
    )
    table_results = db.table("results")

    el_input_path = ENTITY_LINKING_INPUT / f"{iteration}/input.json"
    annotation_results = srsly.read_json(el_input_path)

    annotated_questions = [r["question"][:-1] for r in annotation_results]
    print(f"Retrieved {len(annotated_questions)} annotated questions.")
    search_df = get_search_results_df()
    search_df = process_search_results(search_df)
    processed_questions = {r["question"] for r in table_results}

    table_elements = search_df[["query", "wiki_pages", "linked_entities"]]

    print(f"Retrieved {len(processed_questions)} existing processed questions.")
    if len(table_elements) != 0:
        print(
            f"Total dataset progress: {len(processed_questions) / len(table_elements) * 100:.2f}%"
        )
    buffer = []
    annotated_table_elements = table_elements[:][table_elements["query"].isin(annotated_questions)]
    filtered_table_elements = annotated_table_elements.loc[
        ~annotated_table_elements["query"].isin(processed_questions)
    ]
    with WorkerPool(
        n_jobs=n_jobs, start_method="threading", shared_objects=EntityLinkingClient()
    ) as pool:
        for result in pool.imap(
            process_question,
            list(
                zip(
                    filtered_table_elements["query"],
                    filtered_table_elements["linked_entities"],
                    filtered_table_elements["wiki_pages"],
                )
            ),
            progress_bar=True,
            chunk_size=BUFFER_CHUNK_SIZE,
        ):
            buffer.append(result)
            if len(buffer) >= BUFFER_CHUNK_SIZE:
                print(f"{get_current_time_str()}: Inserting to db...")
                assert len(buffer) == BUFFER_CHUNK_SIZE
                insert_to_table_and_clean_buffer(buffer, table_results)
    insert_to_table_and_clean_buffer(buffer, table_results)


typer.run(main)
