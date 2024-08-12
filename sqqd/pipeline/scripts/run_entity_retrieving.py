import json
import os
from typing import Dict, List, Optional

import pandas as pd
import requests
import typer
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3 import Retry

from sqqd.defaults import ENTITIES_PATH, VITAL_ARTICLES_PATH

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"


def init_session() -> requests.Session:
    adapter = HTTPAdapter(max_retries=Retry(backoff_factor=1, total=20))
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http


def get_id_from_title(session: requests.Session, title: str) -> Optional[str]:
    api_url = "https://en.wikipedia.org/w/api.php"
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
    pages = data.get("query", {}).get("pages", {})
    item = pages.get(next(iter(pages), "-1"), {}).get("pageprops", {})
    return str(item.get("wikibase_item"))


def get_entity_labels_list(filename: str) -> List[str]:
    vital_articles_df = pd.read_csv(VITAL_ARTICLES_PATH / filename)
    entity_labels = [str(title) for title in vital_articles_df["title"]]
    return entity_labels


def get_entity_ids_dict(entity_labels_list: List[str]) -> Dict[str, str]:
    entity_ids_dict = {}
    session = init_session()
    for entity_label in tqdm(entity_labels_list):
        entity_id = get_id_from_title(session, entity_label)
        if entity_id:
            entity_ids_dict[entity_label] = entity_id
        else:
            print(f"Skipping entity: '{entity_label}' due to the exception.")
    return entity_ids_dict


def main() -> None:
    input_filename = "vital_articles_level_4.csv"
    entity_labels_list = get_entity_labels_list(input_filename)
    entity_ids_dict = get_entity_ids_dict(entity_labels_list)

    output_filename = "vital_articles_level_4.json"
    ENTITIES_PATH.mkdir(exist_ok=True)
    file_path = ENTITIES_PATH / output_filename
    with open(file_path, "w") as f:
        json.dump(entity_ids_dict, f, indent=4, ensure_ascii=False)


typer.run(main)
