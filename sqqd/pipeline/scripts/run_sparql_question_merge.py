import itertools

import typer
from tinydb import TinyDB

from gqqd.utils.utils import insert_to_table_and_clean_buffer
from sqqd.defaults import SPARQL_QUESTIONS, TEMPLATE_LIST


def main() -> None:
    merged_db = TinyDB(SPARQL_QUESTIONS / "db.json", indent=4, ensure_ascii=False)
    merged_db_table = merged_db.table("results")

    db_file_paths = [
        SPARQL_QUESTIONS / f"results_for_{template}.json" for template in TEMPLATE_LIST
    ]

    buffer = []
    buffer_size = 40
    id_generator = itertools.count(start=1)

    for db_file_path in db_file_paths:
        db = TinyDB(db_file_path, indent=4, ensure_ascii=False)
        table_results = db.table("results")
        for item in table_results.all():
            item.doc_id = id_generator.__next__()
            buffer.append(dict(item))
            if len(buffer) > buffer_size:
                insert_to_table_and_clean_buffer(buffer, merged_db_table)
    insert_to_table_and_clean_buffer(buffer, merged_db_table)


typer.run(main)
