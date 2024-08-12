import json

import srsly
import typer
from rich import print

from gqqd.defaults import CORRECT_PREFIXES


def reduce(queries: list[str], dataset: str, n: int):
    existing_queries = []
    for n_ in range(1, n):
        existing_queries += srsly.read_json(
            CORRECT_PREFIXES / "annotated" / f"{dataset}_{n_}t.json"
        )
    reduced = [q for q in queries if not any(q.startswith(eq) for eq in existing_queries)]
    print(f"Reduced by {len(queries) - len(reduced)} existing queries.")
    return reduced


def main(dataset: str = typer.Option(...), n: int = typer.Option(...)):
    queries = srsly.read_json(CORRECT_PREFIXES / "to_annotate" / f"{dataset}_{n}t.json")

    queries = reduce(queries, dataset, n)
    print(f"Unique queries:\t{len(queries)}")

    output_path = CORRECT_PREFIXES / "to_annotate" / f"{dataset}_{n}t_reduced.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(
            queries,
            f,
            indent=2,
            ensure_ascii=False,
        )


typer.run(main)
