from dataclasses import asdict, dataclass
from typing import List

import typer
from tinydb import TinyDB

from sqqd.defaults import ANNOTATION_PATH, OUTPUT_PATH


@dataclass
class AnnotationItem:
    id: str
    primary_question: str
    inflected_question: str
    paraphrased_question: str
    answer_labels: List[str]
    annotation: int = 0


def main() -> None:
    results_db = TinyDB(OUTPUT_PATH / "results_db.json", indent=4, ensure_ascii=False)
    table_results = results_db.table("results")
    ANNOTATION_PATH.mkdir(exist_ok=True)
    annotation_db = TinyDB(ANNOTATION_PATH / "db.json", indent=4, ensure_ascii=False)
    annotation_db_table = annotation_db.table("results")
    annotation_items = []
    for item in table_results.all():
        annotation_item = AnnotationItem(
            id=item["id"],
            primary_question=item["primary_question"],
            inflected_question=item["inflected_question"],
            paraphrased_question=item["paraphrased_question"],
            answer_labels=item["answer_labels"],
        )
        annotation_items.append(asdict(annotation_item))
    annotation_db_table.insert_multiple(annotation_items)


typer.run(main)
