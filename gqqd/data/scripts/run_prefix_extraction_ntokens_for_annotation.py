import json
from collections import Counter

import typer
from rich import print

from gqqd.data.datasets_loaders import CzyWieszLoader, PoquadLoader
from gqqd.defaults import CORRECT_PREFIXES
from gqqd.pipeline.prefix_extractors import LemmatizedNTokenPrefixExtractor


def main(dataset: str = typer.Option(...), n: int = typer.Option(...)):
    if dataset == "czywiesz":
        loader = CzyWieszLoader()
    elif dataset == "poquad":
        loader = PoquadLoader()
    else:
        raise ValueError

    questions = loader.load().question.tolist()

    extractor = LemmatizedNTokenPrefixExtractor(n, "pl_core_news_lg")
    counted_queries = Counter(extractor.extract(questions))
    counted_queries = {k: c for k, c in counted_queries.items() if c > 1}
    assert None not in counted_queries
    assert "" not in counted_queries
    queries = sorted(counted_queries, key=counted_queries.get, reverse=True)
    print(f"Unique queries:\t{len(queries)}")

    output_path = CORRECT_PREFIXES / "to_annotate" / f"{dataset}_{n}t.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(
            queries,
            f,
            indent=2,
            ensure_ascii=False,
        )


typer.run(main)
