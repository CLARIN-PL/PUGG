import json
import traceback
from pathlib import Path

import srsly
import tqdm
import typer
from rich import print
from tinydb import TinyDB

from gqqd.auto_annotation.chatgpt_annotator import ChatGPTClient
from gqqd.defaults import ANNOTATED_PATH, CHATGPT_CONFIG
from gqqd.utils.utils import get_current_time_str, insert_to_table_and_clean_buffer


def main(
    iteration: int = typer.Option(0),
    input_path: Path = typer.Option(
        "data/datasets/suggestion_dataset/results/annotated/qa_reranked.json"
    ),
    output_path: Path = typer.Option(None),
) -> None:
    print(locals())

    if output_path is None:
        output_path = ANNOTATED_PATH / f"gpt_responses_iteration_{iteration}.json"

    with open(input_path, "r") as f:
        data = json.load(f)

    db = TinyDB(output_path, indent=4, ensure_ascii=False)
    table_results = db.table("results")
    done_questions = {r["question"] for r in table_results}

    config = srsly.read_yaml(CHATGPT_CONFIG)
    annotator = ChatGPTClient(config["messages"], config["final_message_schema"])

    buffer = []
    for i, entry in enumerate(tqdm.tqdm(data)):
        question = entry["question"]
        if question in done_questions:
            continue

        if iteration < len(entry["passages"]):
            entry["passage"] = list(
                sorted(entry["passages"], key=lambda x: x["reranker_score"], reverse=True)
            )[iteration]
        else:
            print(
                f"{get_current_time_str()}: Skipping {i} question: '{question}' due "
                f"to insufficient number of passages."
            )
            continue
        entry.pop("passages")

        try:
            r = annotator.get_response(question=question, context=entry["passage"]["text"])[1]
        except Exception:
            traceback.print_exc()
            print(
                f"{get_current_time_str()}: Skipping {i} question: '{question}' due to the exception."
            )
            continue

        entry["passage"]["chatgpt_response"] = r
        buffer.append(entry)
        if len(buffer) >= 250:
            print(f"{get_current_time_str()}: Inserting to db...")
            assert len(buffer) == 250
            insert_to_table_and_clean_buffer(buffer, table_results)
    insert_to_table_and_clean_buffer(buffer, table_results)


typer.run(main)
