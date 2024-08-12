import json
import os
from pathlib import Path
from typing import Dict, List

import typer
from tqdm import tqdm

from sqqd.api.wikidata_query_client import WikidataSPARQLClient
from sqqd.defaults import ENTITIES_PATH, PROPERTIES_PATH

WIKIDATA_QUERY_CLIENT = WikidataSPARQLClient(agent=os.getenv("SPARQL_USER_AGENT"))


def get_properties_dict(entity_ids_list: List[str]) -> Dict[str, int]:
    properties_dict: Dict[str, int] = {}
    for entity_id in tqdm(entity_ids_list):
        query = f"""
            SELECT DISTINCT ?relation WHERE {{
                wd:{entity_id} ?relation ?relatedEntity .
                FILTER (STRSTARTS(STR(?relatedEntity), "http://www.wikidata.org/entity/Q"))
            }}
        """
        results = WIKIDATA_QUERY_CLIENT.get_query_results(query)
        if results:
            for item in results.get("results", {}).get("bindings", []):
                relation_value = item["relation"]["value"][36:]
                properties_dict[relation_value] = properties_dict.get(relation_value, 0) + 1
    return properties_dict


def save_properties_to_file(properties_dict: Dict[str, int], file_path: Path) -> None:
    sorted_dict = dict(sorted(properties_dict.items(), key=lambda item: item[1], reverse=True))
    with open(file_path, "w") as f:
        json.dump(sorted_dict, f, indent=4, ensure_ascii=False)


def main() -> None:
    with open(ENTITIES_PATH / "vital_articles_level_4.json", "r") as f:
        entity_ids_dict = json.load(f)
    properties_dict = get_properties_dict(list(entity_ids_dict.values()))

    PROPERTIES_PATH.mkdir(exist_ok=True)
    save_properties_to_file(properties_dict, PROPERTIES_PATH / "all_properties.json")


typer.run(main)
