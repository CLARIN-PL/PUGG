import pandas as pd
import typer
from tinydb import TinyDB

from sqqd.defaults import (
    CHATGPT_INFLECTION_RESULTS,
    CHATGPT_PARAPHRASE_RESULTS,
    OUTPUT_PATH,
    SPARQL_QUESTIONS,
)


def main() -> None:
    base_questions = TinyDB(SPARQL_QUESTIONS / "db.json", indent=4, ensure_ascii=False)
    table_base_questions = base_questions.table("results")
    inflected_questions = TinyDB(
        CHATGPT_INFLECTION_RESULTS / "db.json", indent=4, ensure_ascii=False
    )
    table_inflected_questions = inflected_questions.table("results")
    paraphrased_questions = TinyDB(
        CHATGPT_PARAPHRASE_RESULTS / "db.json", indent=4, ensure_ascii=False
    )
    table_paraphrased_questions = paraphrased_questions.table("results")

    base_question_df = pd.DataFrame(table_base_questions.all())
    inflected_question_df = pd.DataFrame(table_inflected_questions.all())
    paraphrased_question_df = pd.DataFrame(table_paraphrased_questions.all())

    results_df = base_question_df.merge(inflected_question_df, on="primary_question").merge(
        paraphrased_question_df, on="inflected_question", how="left"
    )

    new_column_order = [
        "id",
        "base_entity",
        "template",
        "sparql_query",
        "primary_question",
        "inflected_question",
        "paraphrased_question",
        "answer_ids",
        "answer_labels",
        "question_entity_ids",
        "question_entity_labels",
        "relation_ids",
        "relation_labels",
        "time",
    ]
    results_df = results_df[new_column_order]

    OUTPUT_PATH.mkdir(exist_ok=True)
    results_db = TinyDB(OUTPUT_PATH / "results_db.json", indent=4, ensure_ascii=False)
    table_results = results_db.table("results")
    table_results.insert_multiple(results_df.to_dict(orient="records"))


typer.run(main)
