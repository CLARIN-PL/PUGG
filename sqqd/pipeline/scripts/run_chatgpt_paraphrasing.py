from dataclasses import dataclass

import typer

from sqqd.api.chatgpt_rephrasing.question_processing_pipeline import process_questions
from sqqd.defaults import (
    CHATGPT_INFLECTION_RESULTS,
    CHATGPT_PARAPHRASE_CONFIG,
    CHATGPT_PARAPHRASE_RESULTS,
)


@dataclass
class ParaphrasedQuestionResult:
    inflected_question: str
    paraphrased_question: str


def main() -> None:
    process_questions(
        CHATGPT_INFLECTION_RESULTS,
        CHATGPT_PARAPHRASE_RESULTS,
        CHATGPT_PARAPHRASE_CONFIG,
        "inflected_question",
        ParaphrasedQuestionResult,
        0.2,
    )


typer.run(main)
