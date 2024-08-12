import pytest
from datasets import load_dataset

GENERAL_KBQA_MRC_DATASETS = [
    ("clarin-pl/PUGG", "kbqa_all"),
    ("clarin-pl/PUGG", "kbqa_natural"),
    ("clarin-pl/PUGG", "kbqa_template-based"),
    ("clarin-pl/PUGG", "mrc"),
]

GENRAL_IR_DATASETS = [
    ("clarin-pl/PUGG", "ir_corpus"),
    ("clarin-pl/PUGG", "ir_queries"),
    ("clarin-pl/PUGG", "ir_qrels"),
]

KBQA_DATASETS = [
    ("clarin-pl/PUGG_KBQA", None),
    ("clarin-pl/PUGG_KBQA", "all"),
    ("clarin-pl/PUGG_KBQA", "natural"),
    ("clarin-pl/PUGG_KBQA", "template-based"),
]

MRC_DATASETS = [("clarin-pl/PUGG_MRC", None)]

IR_DATASETS = [
    ("clarin-pl/PUGG_IR", "corpus"),
    ("clarin-pl/PUGG_IR", "queries"),
    ("clarin-pl/PUGG_IR", "qrels"),
]

KG_CONFIGS = [
    "1H_aliases",
    "1H_attributes",
    "1H_descriptions",
    "1H_labels_en",
    "1H_labels_pl",
    "1H_times",
    "1H_triples",
    "2H_aliases",
    "2H_attributes",
    "2H_descriptions",
    "2H_labels_en",
    "2H_labels_pl",
    "2H_times",
    "2H_triples",
]


@pytest.mark.parametrize(
    "dataset_name, config_name", GENERAL_KBQA_MRC_DATASETS + KBQA_DATASETS + MRC_DATASETS
)
def test_load_dataset_general_kbqa_ir(dataset_name, config_name):
    dataset = load_dataset(dataset_name, config_name)
    assert "train" in dataset
    assert "test" in dataset
    assert len(dataset["train"]) > 0
    assert len(dataset["test"]) > 0


@pytest.mark.parametrize("dataset_name, config_name", GENRAL_IR_DATASETS + IR_DATASETS)
def test_load_dataset_ir(dataset_name, config_name):
    dataset = load_dataset(dataset_name, config_name)
    assert "train" not in dataset
    assert "test" in dataset
    assert len(dataset["test"]) > 0


@pytest.mark.parametrize("config_name", KG_CONFIGS)
def test_load_dataset_kg(config_name):
    dataset = load_dataset("clarin-pl/PUGG_KG", config_name)
    assert "train" in dataset
    assert len(dataset["train"]) > 0
