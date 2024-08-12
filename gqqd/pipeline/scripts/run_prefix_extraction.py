import json

import srsly
import typer
from rich import print
from rich.table import Table

from gqqd.data.datasets_loaders import CzyWieszLoader, PoquadLoader
from gqqd.defaults import QUESTION_PREFIXES
from gqqd.pipeline.prefix_extractors import SpacyPrefixExtractor, TransformerPrefixExtractor


def main(dataset: str = typer.Option(...)):
    if dataset == "czywiesz":
        loader = CzyWieszLoader()
    elif dataset == "poquad":
        loader = PoquadLoader()
    else:
        raise ValueError

    questions = loader.load().question.tolist()

    spacy_extractor_sm = SpacyPrefixExtractor("pl_core_news_sm")
    spacy_extractor_lg = SpacyPrefixExtractor("pl_core_news_lg")
    transformer_extractor = TransformerPrefixExtractor("Babelscape/wikineural-multilingual-ner")
    question_queries = []

    table = Table(
        "pl_core_news_sm",
        "pl_core_news_lg",
        "Babelscape/wikineural-multilingual-ner",
        title="NER disagreement",
        show_lines=True,
    )

    for q1, q2, q3 in zip(
        spacy_extractor_sm.extract(questions),
        spacy_extractor_lg.extract(questions),
        transformer_extractor.extract(questions),
    ):
        if not (q1 == q2 == q3):
            table.add_row(q1, q2, q3)
        question_queries.append([q1, q2, q3])

    print(table)

    ner_agreement = sum(q1 == q2 == q3 for q1, q2, q3 in question_queries) / len(question_queries)
    print(f"NER agreement: {ner_agreement}")

    unique_queries = set()
    for q in question_queries:
        unique_queries.update(q)
    unique_queries.remove(None)
    unique_queries.remove("")
    print(f"Unique queries:\t{len(unique_queries)}")

    output_path = QUESTION_PREFIXES / f"{dataset}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    srsly.write_json(output_path, list(unique_queries))

    with output_path.open("w") as f:
        json.dump(list(unique_queries), f, indent=4, ensure_ascii=False)


typer.run(main)
