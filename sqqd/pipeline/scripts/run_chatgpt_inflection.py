from dataclasses import dataclass

import typer

from sqqd.api.chatgpt_rephrasing.question_processing_pipeline import process_questions
from sqqd.defaults import CHATGPT_INFLECTION_CONFIG, CHATGPT_INFLECTION_RESULTS, SPARQL_QUESTIONS


@dataclass
class InflectedQuestionResult:
    primary_question: str
    inflected_question: str


def main() -> None:
    process_questions(
        SPARQL_QUESTIONS,
        CHATGPT_INFLECTION_RESULTS,
        CHATGPT_INFLECTION_CONFIG,
        "primary_question",
        InflectedQuestionResult,
        0.9,
    )


typer.run(main)
