import itertools
import json
import traceback
from dataclasses import asdict, dataclass
from typing import Any

import srsly
import typer
from dotenv import load_dotenv
from rich import print
from tinydb import TinyDB

from gqqd.api.search_results_client import AllKeysUsed, GoogleSearchResultsClient
from gqqd.defaults import CREDENTIALS_ENV, SEARCH_RESULTS, SUGGESTIONS_PATH
from gqqd.utils.utils import get_current_time_str, insert_to_table_and_clean_buffer


@dataclass
class SearchResult:
    query: str
    result: dict[str, Any]
    time: str


def load_suggestions() -> set[str]:
    suggestions = set()
    for path in SUGGESTIONS_PATH.glob("*.json"):
        suggestions.update(
            set(itertools.chain.from_iterable(x["suggestions"] for x in srsly.read_json(path)))
        )
    return suggestions


def main(
    cse_id: str = typer.Argument(..., envvar="CUSTOM_SEARCH_ID"),
    api_keys: str = typer.Argument(..., envvar="GOOGLE_API_KEYS"),
) -> None:
    suggestions = load_suggestions()

    db = TinyDB(SEARCH_RESULTS / "db.json", indent=4, ensure_ascii=False)
    table_results = db.table("results")

    done_queries = {r["query"] for r in table_results}
    print(f"Retrieved {len(done_queries)} existing queries.")
    print(f"Total dataset progress: {len(done_queries)/len(suggestions) *100:.2f}%")
    suggestions = suggestions - done_queries

    api_keys = json.loads(api_keys)
    client = GoogleSearchResultsClient(api_keys, cse_id)

    buffer = []

    for i, query in enumerate(suggestions):
        try:
            result = SearchResult(
                query=query,
                result=client.search(query, num=10),
                time=get_current_time_str(),
            )
        except AllKeysUsed:
            insert_to_table_and_clean_buffer(buffer, table_results)
            raise typer.Exit()
        except Exception:
            traceback.print_exc()
            print(f"{get_current_time_str()}: Skipping {i} query: '{query}' due to the exception.")
            continue
        buffer.append(asdict(result))
        done_queries.add(query)
    if len(buffer) >= 50:
        print(f"{get_current_time_str()}: Inserting to db...")
        assert len(buffer) == 50
        insert_to_table_and_clean_buffer(buffer, table_results)

    insert_to_table_and_clean_buffer(buffer, table_results)


load_dotenv(CREDENTIALS_ENV)
typer.run(main)
