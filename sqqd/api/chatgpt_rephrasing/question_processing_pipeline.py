import difflib
from dataclasses import asdict
from pathlib import Path

import openai.error
import srsly
from tinydb import TinyDB
from tqdm import tqdm

from gqqd.utils.utils import insert_to_table_and_clean_buffer
from sqqd.api.chatgpt_rephrase_client import ChatGPTClient


def process_questions(
    input_folder: Path,
    output_folder: Path,
    config_path: Path,
    response_field: str,
    ResultClass: type,
    min_levenstein_distance: float,
) -> None:
    config = srsly.read_yaml(config_path)
    chat_gpt_client = ChatGPTClient(config["messages"])
    output_folder.mkdir(exist_ok=True)
    db = TinyDB(output_folder / "db.json", indent=4, ensure_ascii=False)
    table_results = db.table("results")

    question_db = TinyDB(input_folder / "db.json", indent=4, ensure_ascii=False)
    table_questions = question_db.table("results")
    all_questions = [r[response_field] for r in table_questions]
    processed_questions = {r[response_field] for r in table_results}
    print(f"Retrieved {len(processed_questions)} existing processed questions.")

    filtered_questions = [q for q in all_questions if q not in processed_questions]
    buffer = []
    for question in tqdm(filtered_questions):
        try:
            question_result = chat_gpt_client.get_response(question)
        except openai.error.Timeout as e:
            print(f"Failed to process question: {question}")
            print(e)
            continue
        if question_result is not None:
            if (
                difflib.SequenceMatcher(None, question, question_result).ratio()
                > min_levenstein_distance
            ):
                result = ResultClass(question, question_result)
                buffer.append(asdict(result))
                if len(buffer) >= 10:
                    insert_to_table_and_clean_buffer(buffer, table_results)
    insert_to_table_and_clean_buffer(buffer, table_results)
