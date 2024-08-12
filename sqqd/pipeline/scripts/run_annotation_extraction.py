import json

import typer
from tinydb import TinyDB

from sqqd.defaults import ANNOTATION_PATH, OUTPUT_PATH


def main() -> None:
    annotation_results_db = TinyDB(
        ANNOTATION_PATH / "annotated_db.json", indent=4, ensure_ascii=False
    )
    annotation_results_db_table = annotation_results_db.table("results")
    annotation_ids_to_keep = {
        item["id"] for item in annotation_results_db_table.all() if item["annotation"] == 1
    }

    results_db = TinyDB(OUTPUT_PATH / "results_db.json", indent=4, ensure_ascii=False)
    table_results = results_db.table("results")

    results_filtered = []
    keys_to_remove = ["base_entity", "primary_question", "inflected_question", "time"]

    for entry in table_results.all():
        if entry["id"] in annotation_ids_to_keep:
            for key in keys_to_remove:
                entry.pop(key, None)
            results_filtered.append(entry)

    output_data_path = OUTPUT_PATH / "results_db_filtered.json"
    with open(output_data_path, "w", encoding="utf-8") as file:
        json.dump(results_filtered, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    typer.run(main)
