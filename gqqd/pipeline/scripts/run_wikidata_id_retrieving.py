import itertools
import os
import traceback

import requests
import srsly
import typer
from mpire import WorkerPool
from requests.adapters import HTTPAdapter
from tinydb import TinyDB
from urllib3 import Retry

from gqqd.defaults import ENTITY_LINKING_INPUT, ENTITY_LINKING_PROCESSED, WIKIDATA_ITEM_IDS
from gqqd.utils.utils import get_current_time_str, insert_to_table_and_clean_buffer

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"


def init_session() -> requests.Session:
    adapter = HTTPAdapter(max_retries=Retry(backoff_factor=1, total=20))
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http


def get_redirected_id(session: requests.Session, title: str) -> dict[str, str | int]:
    api_url = "https://pl.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageprops",
        "ppprop": "wikibase_item",
        "redirects": "1",
        "format": "json",
        "titles": title,
    }
    if os.getenv("SPARQL_USER_AGENT") is not None:
        header = {"User-Agent": os.getenv("SPARQL_USER_AGENT")}
        response = session.get(api_url, params=params, headers=header)
    else:
        response = session.get(api_url, params=params)
    response.raise_for_status()
    data = response.json()
    if "pages" not in data["query"]:
        return {"title": title, "wikidata_id": None}
    pages = data["query"]["pages"]
    [(key, item)] = pages.items()
    if key != "-1" and "pageprops" in item:
        return {
            "title": title,
            "wikidata_id": item["pageprops"]["wikibase_item"],
        }
    else:
        return {"title": title, "wikidata_id": None}


def process_link(session: requests.Session, wiki_link: str) -> dict[str, str | int] | None:
    try:
        return get_redirected_id(session, wiki_link)
    except KeyError:
        traceback.print_exc()
        print(f"{get_current_time_str()}: Skipping link: '{wiki_link}' due to the exception.")
        return None


def main(n_jobs: int = typer.Option(default=500), iteration: int = typer.Option(default=0)) -> None:
    db = TinyDB(
        ENTITY_LINKING_PROCESSED / f"{iteration}/entity_linking_results.json",
        indent=4,
        ensure_ascii=False,
    )
    wiki_results_table = db.table("results")

    WIKIDATA_ITEM_IDS.mkdir(exist_ok=True)
    db = TinyDB(
        ENTITY_LINKING_PROCESSED / f"{iteration}/titles_and_ids.json", indent=4, ensure_ascii=False
    )
    wikidata_ids_results = db.table("results")

    processed_links = {r["title"] for r in wikidata_ids_results}

    print(f"Retrieved {len(processed_links)} existing links.")
    direct_wiki_links = list(
        itertools.chain.from_iterable(entry["direct_pages"] for entry in wiki_results_table)
    )
    associated_wiki_links = list(
        itertools.chain.from_iterable(entry["associated_pages"] for entry in wiki_results_table)
    )

    el_input_path = ENTITY_LINKING_INPUT / f"{iteration}/input.json"
    annotation_results = srsly.read_json(el_input_path)

    answer_wiki_links = list(
        itertools.chain.from_iterable(r["answer_entities"] for r in annotation_results)
    )

    passage_page_wiki_links = [r["passage_page"] for r in annotation_results]

    wiki_links = set(
        direct_wiki_links + associated_wiki_links + answer_wiki_links + passage_page_wiki_links
    )
    print(f"Total dataset progress: {len(processed_links) / len(wiki_links) * 100:.2f}%")

    filtered_links = [link for link in wiki_links if link not in processed_links]

    buffer = []

    session = init_session()
    with WorkerPool(n_jobs=n_jobs, start_method="threading", shared_objects=session) as pool:
        for result in pool.imap(process_link, filtered_links, progress_bar=True, chunk_size=250):
            if result is None:
                continue
            buffer.append(result)
            if len(buffer) >= 250:
                print(f"{get_current_time_str()}: Inserting to db...")
                assert len(buffer) == 250
                insert_to_table_and_clean_buffer(buffer, wikidata_ids_results)
    insert_to_table_and_clean_buffer(buffer, wikidata_ids_results)


typer.run(main)
