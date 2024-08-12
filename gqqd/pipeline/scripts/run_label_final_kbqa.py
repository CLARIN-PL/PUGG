import json
import os
from random import Random

import srsly
from dotenv import load_dotenv
from mpire import WorkerPool
from tqdm import tqdm

from gqqd.api.wikidata import WikidataClient
from gqqd.defaults import FINAL_GQQD_DATASET, ROOT_PATH
from sqqd.api.wikidata_query_client import WikidataSPARQLClient

N_JOBS = 20


def main() -> None:
    load_dotenv(ROOT_PATH / ".env")
    data = srsly.read_json(FINAL_GQQD_DATASET / "kbqa_unlabeled.json")
    entities = set()
    for entry in tqdm(data):
        for entity in entry["answer"] + entry["topic"]:
            entities.add(entity["entity_id"])
    entities_ids = list(entities)
    sparql_client = WikidataSPARQLClient(agent=os.getenv("SPARQL_USER_AGENT"))
    wikidata_client = WikidataClient()
    with WorkerPool(N_JOBS, start_method="threading") as pool:
        labels = pool.map(sparql_client.get_object_name, entities_ids, progress_bar=True)
        is_disambiguation = pool.map(
            wikidata_client.is_disambiguation_page, entities_ids, progress_bar=True
        )
    labels_map = {entity: label for entity, label in zip(entities_ids, labels)}
    is_disambiguation_map = {
        entity: label for entity, label in zip(entities_ids, is_disambiguation)
    }
    i = 0
    final = []
    Random(17).shuffle(data)
    for entry in tqdm(data):
        entry["answer"] = [
            entity for entity in entry["answer"] if not is_disambiguation_map[entity["entity_id"]]
        ]
        entry["topic"] = [
            entity for entity in entry["topic"] if not is_disambiguation_map[entity["entity_id"]]
        ]
        for entity in entry["answer"] + entry["topic"]:
            entity["entity_label"] = labels_map[entity["entity_id"]]
        if len(entry["answer"]) > 0 and len(entry["topic"]) > 0:
            entry["id"] = f"kbqa_natural_{i}"
            final.append(entry)
            i += 1

    with open(FINAL_GQQD_DATASET / "kbqa_labeled.json", "w") as f:
        json.dump(final, f, indent=4, ensure_ascii=False)


main()
