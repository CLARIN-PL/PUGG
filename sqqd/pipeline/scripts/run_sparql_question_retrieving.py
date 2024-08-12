import json
import os
from dataclasses import asdict
from random import Random
from typing import List

import typer
from tinydb import TinyDB
from tqdm import tqdm

from gqqd.utils.utils import insert_to_table_and_clean_buffer
from sqqd.api.sparql_question_client import SPARQLQuestionClient
from sqqd.defaults import ENTITIES_PATH, SPARQL_QUESTIONS, TEMPLATE_LIST


def get_entity_list(entity_number: int, random_seed: int = 42, debug: bool = False) -> List[str]:
    if debug:
        return ["Q79822"]
    with open(ENTITIES_PATH / "vital_articles_level_4.json", "r") as f:
        entity_ids_dict = json.load(f)
    entity_id_list = list(entity_ids_dict.values())

    random_generator = Random(random_seed)
    entity_id_list = random_generator.sample(entity_id_list, entity_number)
    return entity_id_list


def main(
    template_list: List[str] = typer.Option(default=TEMPLATE_LIST),
    entity_number: int = typer.Option(default=1800),
    entries_per_entity_limit: int = typer.Option(default=1),
) -> None:
    SPARQL_QUESTIONS.mkdir(exist_ok=True)
    entity_list = get_entity_list(entity_number)
    buffer = []
    buffer_size = 20

    for template_name in template_list:
        print("Running template:", template_name)
        db = TinyDB(
            SPARQL_QUESTIONS / f"results_for_{template_name}.json", indent=4, ensure_ascii=False
        )
        table_results = db.table("results")
        sparql_client = SPARQLQuestionClient(
            template_name,
            entries_per_entity_limit,
            wikidata_sparql_client_agent=os.getenv("SPARQL_USER_AGENT"),
        )

        processed_entity_list = {r["base_entity"] for r in table_results.all()}
        filtered_entity_list = [e for e in entity_list if e not in processed_entity_list]
        for entity_id in tqdm(filtered_entity_list):
            retrieved_sparql_question_entries = sparql_client.build_questions_from_entity(entity_id)
            if retrieved_sparql_question_entries:
                for entry in retrieved_sparql_question_entries:
                    buffer.append(asdict(entry))
                    if len(buffer) >= buffer_size:
                        insert_to_table_and_clean_buffer(buffer, table_results)
        insert_to_table_and_clean_buffer(buffer, table_results)


typer.run(main)
