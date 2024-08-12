import json
import os
from typing import Optional

import spacy
import typer
from tqdm import tqdm

from sqqd.api.wikidata_query_client import WikidataSPARQLClient
from sqqd.defaults import PROPERTIES_PATH

WIKIDATA_QUERY_CLIENT = WikidataSPARQLClient(agent=os.getenv("SPARQL_USER_AGENT"))
NLP = spacy.load("pl_core_news_lg")


def get_relation_label(relation_id: str) -> Optional[str]:
    relation_label = WIKIDATA_QUERY_CLIENT.get_object_name(relation_id)
    if relation_label is not None:
        doc = NLP(relation_label)
        if not any([token.pos_ != "NOUN" for token in doc]) and relation_id.startswith("P"):
            return relation_label
    return None


def get_label_dict(properties_dict: dict[str, int]) -> dict[str, str]:
    label_dict = {}
    for property_id in tqdm(properties_dict):
        label = get_relation_label(property_id)
        if label is not None:
            label_dict[property_id] = label
    return label_dict


def main() -> None:
    PROPERTIES_PATH.mkdir(exist_ok=True)

    if not (PROPERTIES_PATH / "all_properties.json").exists():
        raise FileNotFoundError("Run sqqd/pipeline/run_properties_retrieving.py first")

    with open(PROPERTIES_PATH / "all_properties.json", "r") as f:
        properties_dict = json.load(f)

    label_dict = get_label_dict(properties_dict)

    with open(PROPERTIES_PATH / "property_labels.json", "w", encoding="utf-8") as f:
        json.dump(label_dict, f, indent=4, ensure_ascii=False)


typer.run(main)
