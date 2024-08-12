from typing import Any, Literal

import srsly

from gqqd.defaults import FINAL_DATASET_KBQA, WIKIDATA_GRAPHS


def load_dataset(
    dataset: Literal["kbqa_natural", "kbqa_template-based"]
) -> dict[str, list[dict[str, Any]]]:
    train = srsly.read_json(FINAL_DATASET_KBQA / dataset / "train.json")
    test = srsly.read_json(FINAL_DATASET_KBQA / dataset / "test.json")
    return {"train": train, "test": test}


def load_graph(hop: int) -> tuple[list[list[str]], dict[str, str]]:
    triples = srsly.read_json(WIKIDATA_GRAPHS / f"hop_{hop}" / "triples.json")
    labels = srsly.read_json(WIKIDATA_GRAPHS / f"hop_{hop}" / "labels_pl.json")
    return triples, labels
