import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import srsly
import typer
from huggingface_hub import DatasetCard, DatasetCardData

from gqqd.defaults import (
    DATASET_CARD_TEMPLATE,
    FINAL_DATASET_IR,
    FINAL_DATASET_KBQA,
    FINAL_DATASET_MRC,
    HF_DATASETS_PATH,
)


def main(dataset: str = typer.Argument(...)) -> None:
    configs: list[dict[str, Any]] | None
    if dataset == "kbqa":
        dataset_path = HF_DATASETS_PATH / "kbqa"
        configs = create_kbqa(dataset_path, use_default=True)
    elif dataset == "mrc":
        dataset_path = HF_DATASETS_PATH / "mrc"
        configs = create_mrc(dataset_path)
    elif dataset == "ir":
        dataset_path = HF_DATASETS_PATH / "ir"
        create_ir(HF_DATASETS_PATH / "ir")
        shutil.copyfile(HF_DATASETS_PATH / "loading_scripts/ir.py", dataset_path / "PUGG_IR.py")
        configs = None
    elif dataset == "general":
        dataset_path = HF_DATASETS_PATH / "general"
        configs_kbqa = create_kbqa(
            dataset_path, use_default=False, config_prefix="kbqa_", use_subdir=True
        )
        configs_mrc = create_mrc(dataset_path, config_prefix="mrc", use_subdir=True)
        configs_ir = create_ir(dataset_path, config_prefix="ir_", use_subdir=True)
        configs = configs_kbqa + configs_mrc + configs_ir
    else:
        raise ValueError(f"Unknown dataset: {dataset}")

    metadata = srsly.read_yaml(HF_DATASETS_PATH / f"metadata/{dataset}.yaml")

    if configs:
        card_data = DatasetCardData(**metadata, configs=configs)
    else:
        card_data = DatasetCardData(**metadata)

    card_config = srsly.read_yaml(HF_DATASETS_PATH / f"readme/config_{dataset}.yaml")

    card = DatasetCard.from_template(card_data, template_path=DATASET_CARD_TEMPLATE, **card_config)
    card.save(dataset_path / "README.md")


def create_kbqa(
    path: Path, use_default: bool, config_prefix: str = "", use_subdir: bool = False
) -> list[dict[str, Any]]:
    if use_subdir:
        path = path / "kbqa"
    for config in ["natural", "template-based"]:
        for subset in ["train", "test"]:
            data = srsly.read_json(FINAL_DATASET_KBQA / f"kbqa_{config}/{subset}.json")
            if config == "natural":
                for entry in data:
                    entry["sparql_query"] = ""
                    entry["sparql_query_template"] = ""
            out_path = path / config
            out_path.mkdir(exist_ok=True, parents=True)
            srsly.write_jsonl(out_path / f"{subset}.jsonl", data)

    configs = []

    for config in ["all", "natural", "template-based"]:
        directory = "*" if config == "all" else config
        if use_subdir:
            config_dir = f"kbqa/{directory}"
        else:
            config_dir = directory
        config_dict: dict[str, Any] = {
            "config_name": config_prefix + config,
            "data_files": [
                {
                    "split": "train",
                    "path": f"{config_dir}/train.jsonl",
                },
                {
                    "split": "test",
                    "path": f"{config_dir}/test.jsonl",
                },
            ],
        }
        if use_default and config == "all":
            config_dict["default"] = True
        configs.append(config_dict)
    return configs


def create_mrc(
    path: Path, config_prefix: str = "", use_subdir: bool = False
) -> list[dict[str, Any]]:
    if use_subdir:
        path = path / "mrc"
    for subset in ["train", "test"]:
        data = srsly.read_json(FINAL_DATASET_MRC / f"{subset}.json")
        path.mkdir(exist_ok=True, parents=True)
        srsly.write_jsonl(path / f"{subset}.jsonl", data)

    configs = []

    if use_subdir:
        config_dir = "mrc/"
        config_name = config_prefix
    else:
        config_dir = ""
        config_name = "default"
    config_dict: dict[str, Any] = {
        "config_name": config_name,
        "data_files": [
            {
                "split": "train",
                "path": f"{config_dir}train.jsonl",
            },
            {
                "split": "test",
                "path": f"{config_dir}test.jsonl",
            },
        ],
    }
    configs.append(config_dict)
    return configs


def create_ir(
    path: Path, config_prefix: str = "", use_subdir: bool = False
) -> list[dict[str, Any]]:
    if use_subdir:
        path = path / "ir"

    configs = []

    for file in ["corpus.jsonl", "queries.jsonl", "qrels/test.tsv"]:
        new_file_path = path / file
        new_file_path.parent.mkdir(exist_ok=True, parents=True)
        if file.endswith(".jsonl"):
            shutil.copyfile(FINAL_DATASET_IR / file, new_file_path)
        else:
            if use_subdir:  # general
                new_file_path = new_file_path.with_suffix(".jsonl")
                data = pd.read_csv(FINAL_DATASET_IR / file, sep="\t").to_dict(orient="records")
                srsly.write_jsonl(new_file_path, data)
            else:
                shutil.copyfile(FINAL_DATASET_IR / file, new_file_path)
        if use_subdir:
            config_dir = "ir/"
        else:
            config_dir = ""

        if file.endswith(".tsv"):
            config_file_path = file.replace(".tsv", ".jsonl")
        else:
            config_file_path = file
        config_dict: dict[str, Any] = {
            "config_name": config_prefix + file.replace("/", ".").split(".")[0],
            "data_files": [
                {
                    "split": "test",
                    "path": f"{config_dir}{config_file_path}",
                }
            ],
        }
        configs.append(config_dict)
    return configs


typer.run(main)
