from dataclasses import asdict, dataclass

import srsly
import typer
from tinydb import TinyDB

from gqqd.defaults import ENTITY_LINKING_INPUT, ENTITY_LINKING_OUTPUT, ENTITY_LINKING_PROCESSED


@dataclass
class EntityLinkingResult:
    q_p_id: str
    q_id: str
    p_id: str
    question: str
    question_direct_entities: list[str]
    question_direct_entities_ids: list[str]
    question_associated_entities: list[str]
    question_associated_entities_ids: list[str]
    passage: str
    passage_page: str
    passage_page_id: str
    answer_entities: list[str]
    answer_entities_ids: list[str]


def retrieve_ids(entities: list[str], wikidata_ids_results_dict: dict[str, dict]) -> list[str]:
    wikidata_ids = []
    for entity in entities:
        try:
            wikidata_ids.append(wikidata_ids_results_dict[entity]["wikidata_id"])
        except KeyError:
            print(f'Entity "{entity}" not found in titles_and_ids file. Skipping.')
    return wikidata_ids


def main(iteration: int = typer.Option(default=0)) -> None:
    wikidata_ids_table = TinyDB(
        ENTITY_LINKING_PROCESSED / f"{iteration}/titles_and_ids.json", indent=4, ensure_ascii=False
    )
    wikidata_ids_table_results = wikidata_ids_table.table("results")
    wikidata_ids_results_dict = {
        entry_data["title"]: entry_data for entry_data in wikidata_ids_table_results
    }

    entity_linking_table = TinyDB(
        ENTITY_LINKING_PROCESSED / f"{iteration}/entity_linking_results.json",
        indent=4,
        ensure_ascii=False,
    )
    entity_linking_table_results = entity_linking_table.table("results")
    entity_linking_results_dict = {
        entry_data["question"]: entry_data for entry_data in entity_linking_table_results
    }

    entity_linking_output_table = TinyDB(
        ENTITY_LINKING_OUTPUT / f"{iteration}/output.json", indent=4, ensure_ascii=False
    )
    entity_linking_output_table_results = entity_linking_output_table.table("results")

    el_input_path = ENTITY_LINKING_INPUT / f"{iteration}/input.json"
    annotation_results = srsly.read_json(el_input_path)

    for annotation_result in annotation_results:
        q_p_id = annotation_result["q_p_id"]
        q_id = annotation_result["q_id"]
        p_id = annotation_result["p_id"]
        question = annotation_result["question"][:-1]
        passage = annotation_result["passage"]
        passage_page = annotation_result["passage_page"]
        if passage_page not in wikidata_ids_results_dict:
            print(f'Passage page "{passage_page}" not found in titles_and_ids file. Skipping.')
            passage_page_id = ""
        else:
            passage_page_id = retrieve_ids([passage_page], wikidata_ids_results_dict)[0]
        answer_entities = annotation_result["answer_entities"]

        answer_entities_ids = retrieve_ids(answer_entities, wikidata_ids_results_dict)

        if question not in entity_linking_results_dict:
            print(f'Question "{question}" not found in titles_and_ids file. Skipping.')
        else:
            question_direct_entities = entity_linking_results_dict[question]["direct_pages"]
            question_direct_entities_ids = retrieve_ids(
                question_direct_entities, wikidata_ids_results_dict
            )
            question_associated_entities = entity_linking_results_dict[question]["associated_pages"]
            question_associated_entities_ids = retrieve_ids(
                question_associated_entities, wikidata_ids_results_dict
            )
            entity_linking_result = EntityLinkingResult(
                q_p_id=q_p_id,
                q_id=q_id,
                p_id=p_id,
                question=question + "?",
                question_direct_entities=question_direct_entities,
                question_direct_entities_ids=question_direct_entities_ids,
                question_associated_entities=question_associated_entities,
                question_associated_entities_ids=question_associated_entities_ids,
                passage=passage,
                passage_page=passage_page,
                passage_page_id=passage_page_id,
                answer_entities=answer_entities,
                answer_entities_ids=answer_entities_ids,
            )
            entity_linking_output_table_results.insert(asdict(entity_linking_result))


typer.run(main)
