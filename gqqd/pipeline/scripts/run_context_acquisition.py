import itertools
import traceback

import typer
from tinydb import TinyDB
from tqdm import tqdm

from gqqd.api.wikipedia_content_client import WikipediaClient
from gqqd.data.loaders import get_search_results_df
from gqqd.defaults import WIKI_RESULTS
from gqqd.utils.utils import get_current_time_str, insert_to_table_and_clean_buffer


def main() -> None:
    wiki_pages = load_pages()

    WIKI_RESULTS.mkdir(exist_ok=True)
    db = TinyDB(WIKI_RESULTS / "db.json", indent=4, ensure_ascii=False)
    table_results = db.table("results")

    done_pages = {r["page"] for r in table_results}
    print(f"Retrieved {len(done_pages)} existing pages.")
    print(f"Total dataset progress: {len(done_pages) / len(wiki_pages) * 100:.2f}%")
    wiki_pages = wiki_pages - done_pages

    buffer = []
    client = WikipediaClient()

    for i, page in enumerate(tqdm(wiki_pages)):
        try:
            links, page_text = client.retrieve_content(page)
            result = {
                "page": page,
                "plain_text": page_text,
                "wiki_links": links,
                "time": get_current_time_str(),
            }
        except Exception:
            traceback.print_exc()
            print(f"{get_current_time_str()}: Skipping {i} page: '{page}' due to the exception. ")
            continue
        buffer.append(result)
        done_pages.add(page)
        if len(buffer) >= 250:
            print(f"{get_current_time_str()}: Inserting to db...")
            assert len(buffer) == 250
            insert_to_table_and_clean_buffer(buffer, table_results)

    insert_to_table_and_clean_buffer(buffer, table_results)


def load_pages() -> set[str]:
    search_df = get_search_results_df()
    wiki_total = set(itertools.chain.from_iterable(search_df["wiki_pages"]))
    wiki_contents = {wiki_page for wiki_page in wiki_total if "Kategoria" not in wiki_page}
    print(
        len(wiki_total) - len(wiki_contents), "pages were removed due to them being category pages."
    )
    return wiki_contents


typer.run(main)
