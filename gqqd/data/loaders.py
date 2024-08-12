import urllib

import pandas as pd
import srsly
from tinydb import TinyDB

from gqqd.defaults import CORRECT_PREFIXES, SEARCH_RESULTS, SUGGESTIONS_PATH, WIKI_RESULTS

WIKIPEDIA_PREFIX = "pl.wikipedia"
WIKIPEDIA_FILE_PREFIX = "Plik:"


def get_query_df() -> pd.DataFrame:
    dfs = {path.stem: pd.read_json(path) for path in SUGGESTIONS_PATH.glob("*.json")}
    for dataset_name, df in dfs.items():
        df.insert(0, "dataset", dataset_name)
    return pd.concat(dfs.values(), ignore_index=True)


def get_suggestions_df() -> pd.DataFrame:
    df = get_query_df().explode("suggestions").dropna().reset_index(drop=True)
    df["query"] = df["query"].str.strip()
    return df


def get_search_results_df(debug: bool = False) -> pd.DataFrame:
    db_path = SEARCH_RESULTS / "testing_db.json" if debug else SEARCH_RESULTS / "db.json"
    search_df = pd.json_normalize(list(TinyDB(db_path).table("results")), sep=".")
    search_df["result.items"] = [pd.json_normalize(x) for x in search_df["result.items"]]
    for items_df in search_df["result.items"]:
        items_df["is_wikipedia"] = items_df.displayLink.str.contains(
            WIKIPEDIA_PREFIX
        ) & ~items_df.link.str.split("/wiki/").apply(lambda x: x[-1]).str.startswith(
            WIKIPEDIA_FILE_PREFIX
        )
    search_df["results.wikipedia_positions"] = [
        list(items_df[items_df["is_wikipedia"]].index) for items_df in search_df["result.items"]
    ]
    search_df["results.min_wikipedia_position"] = [
        min(x) if len(x) else None for x in search_df["results.wikipedia_positions"]
    ]
    search_df["wiki_links"] = [
        [urllib.parse.unquote(link) for link in items[items.is_wikipedia]["link"]]
        for items in search_df["result.items"]
    ]
    search_df["wiki_pages"] = [
        [urllib.parse.unquote(link.split("/wiki/")[-1].replace("_", " ")) for link in links]
        for links in search_df["wiki_links"]
    ]
    return search_df


def get_correct_prefixes() -> list[str]:
    data = [srsly.read_json(path) for path in (CORRECT_PREFIXES / "annotated").glob("*.json")]
    return [prefix + " " for prefixes in data for prefix in prefixes]


def load_wiki_content_df(filter_not_striped: bool = True) -> pd.DataFrame:
    df = pd.DataFrame(
        TinyDB(WIKI_RESULTS / "db_fixed.json", indent=4, ensure_ascii=False).table("results")
    )
    if filter_not_striped:
        df = df[(df.plain_text.str.len() - df.plain_text.str.strip().str.len()) == 0]
    return df
