from pathlib import Path
from typing import Any

import srsly
import typer
from huggingface_hub import DatasetCard, DatasetCardData

from gqqd.defaults import HF_DATASETS_PATH, KG_CARD_TEMPLATE, WIKIDATA_GRAPHS


def main(hops: list[int] = typer.Option(...)) -> None:
    out_path = HF_DATASETS_PATH / "kg"
    out_path.mkdir(parents=True, exist_ok=True)

    configs = []
    for hop in hops:
        configs.extend(create_dataset_for_hop(hop, out_path))

    card_config = srsly.read_yaml(HF_DATASETS_PATH / "metadata/kg.yaml")
    card_data = DatasetCardData(
        **card_config,
        configs=configs,
    )
    card_config = srsly.read_yaml(HF_DATASETS_PATH / "readme/config_kg.yaml")
    card = DatasetCard.from_template(card_data, template_path=KG_CARD_TEMPLATE, **card_config)
    card.save(out_path / "README.md")


def create_dataset_for_hop(hop: int, out_path: Path) -> list[dict[str, Any]]:
    path = WIKIDATA_GRAPHS / f"hop_{hop}"
    out_path = out_path / str(hop)
    out_path.mkdir(parents=True, exist_ok=True)
    if hop > 0:
        config_prefix = f"{hop}H"
    else:
        raise ValueError()

    configs = []
    for filepath in path.rglob("*.json"):
        print(filepath)
        data = get_data(filepath)
        srsly.write_jsonl(out_path / f"{filepath.stem}.jsonl", data)

        config_dict: dict[str, Any] = {
            "config_name": f"{config_prefix}_{filepath.stem}",
            "data_files": [
                {
                    "split": "train",
                    "path": f"{hop}/{filepath.stem}.jsonl",
                },
            ],
        }
        configs.append(config_dict)

    return configs


def get_data(path: Path) -> list[dict[str, Any]]:
    org_data = srsly.read_json(path)
    match path.stem:
        case "aliases":
            data = [
                {"entity": entity, "aliases": aliases_} for entity, aliases_ in org_data.items()
            ]
        case "attributes":
            data = [{"entity": h, "relation": r, "value": v} for h, r, v in org_data]
        case "descriptions":
            data = [{"entity": e, "description": d} for e, d in org_data.items()]
        case "labels_en":
            data = [{"entity": e, "label_en": l} for e, l in org_data.items()]
        case "labels_pl":
            data = [{"entity": e, "label_pl": l} for e, l in org_data.items()]
        case "times":
            data = [{"entity": e, "relation": r, **time} for e, r, time in org_data]
        case "triples":
            data = [{"head": h, "relation": r, "tail": t} for h, r, t in org_data]
        case _:
            raise ValueError()
    return data


typer.run(main)
