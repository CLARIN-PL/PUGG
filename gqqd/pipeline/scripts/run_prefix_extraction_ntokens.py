import json
from collections import Counter

import typer
from rich import print

from gqqd.data.datasets_loaders import CzyWieszLoader, PoquadLoader
from gqqd.defaults import QUESTION_PREFIXES
from gqqd.pipeline.prefix_extractors import NTokenPrefixExtractor


def main(dataset: str = typer.Option(...), n: int = typer.Option(...)):
    if dataset == "czywiesz":
        loader = CzyWieszLoader()
    elif dataset == "poquad":
        loader = PoquadLoader()
    else:
        raise ValueError

    questions = loader.load().question.tolist()

    extractor = NTokenPrefixExtractor(n)
    counted_queries = Counter(extractor.extract(questions))
    assert None not in counted_queries
    assert "" not in counted_queries
    print(f"Unique queries:\t{len(counted_queries)}")

    output_path = QUESTION_PREFIXES / f"{dataset}_{n}t.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(
            list(sorted(counted_queries, key=counted_queries.get, reverse=True)),
            f,
            indent=4,
            ensure_ascii=False,
        )


typer.run(main)
