import json
from pathlib import Path

import tqdm
import typer
from tinydb import TinyDB

from gqqd.auto_annotation.chatgpt_annotator import ChatGPTAnnotator
from gqqd.defaults import ANNOTATED_PATH


def main(
    iteration: int = typer.Option(0),
    input_path: Path = typer.Option(None),
    output_path: Path = typer.Option(None),
) -> None:
    print(locals())

    if input_path is None:
        input_path = ANNOTATED_PATH / f"gpt_responses_iteration_{iteration}.json"

    if output_path is None:
        output_path = ANNOTATED_PATH / f"gpt_auto_annotated_iteration_{iteration}.json"

    db = TinyDB(input_path, indent=4, ensure_ascii=False)
    table_results = db.table("results")
    data = list(table_results)

    annotator = ChatGPTAnnotator()
    new_data = []
    for idx, entry in enumerate(tqdm.tqdm(data)):
        context = entry["passage"]["text"]
        gpt_message = entry["passage"]["chatgpt_response"]["choices"][0]["message"]["content"]
        entry["passage"].pop("chatgpt_response")

        annotation = annotator.get_annotation(gpt_message, context)
        if annotation is not None:
            entry["passage"]["gpt_answer"] = annotation["gpt_answer"]
            entry["passage"]["span"] = annotation["span"]
            new_data.append(entry)
    with open(output_path, "w") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)


typer.run(main)
