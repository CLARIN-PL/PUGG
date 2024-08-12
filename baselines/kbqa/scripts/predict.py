import json
from typing import Optional

import pandas as pd
import srsly
import typer
from dotenv import load_dotenv
from tqdm import tqdm

from baselines.defaults import KBQA_BASELINES_PATH, KBQA_PROMPT_CONFIGS_DIR
from baselines.kbqa.data import load_dataset
from baselines.kbqa.predictor import GPTClient
from gqqd.defaults import ROOT_PATH


def main(
    dataset_name: str = typer.Option(...),
    predictor_mode: str = typer.Option(...),
    model: str = typer.Option(...),
    graph_hop: Optional[int] = typer.Option(None),
    retriever_hop: Optional[int] = typer.Option(None),
    k: Optional[int] = typer.Option(None),
) -> None:
    if (ROOT_PATH / "credentials.env").exists():
        load_dotenv(ROOT_PATH / "credentials.env")

    if predictor_mode == "knowledge":
        assert graph_hop is not None and retriever_hop is not None and k is not None
    elif predictor_mode == "noknowledge":
        assert graph_hop is None and retriever_hop is None and k is None
    else:
        raise ValueError(f"Unknown predictor mode: {predictor_mode}")
    output_path = (
        KBQA_BASELINES_PATH
        / "predictions"
        / predictor_mode
        / f"graph_hop_{graph_hop}"
        / model
        / dataset_name
        / f"retriever_hop_{retriever_hop}"
        / f"k_{k}"
    )
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Predicting on {dataset_name}...")
    dataset = load_dataset(dataset_name)["test"]
    df = pd.DataFrame(dataset)

    if predictor_mode == "knowledge":
        subgraphs = srsly.read_json(
            (
                KBQA_BASELINES_PATH
                / "subgraphs"
                / f"graph_hop_{graph_hop}"
                / dataset_name
                / f"retriever_hop_{retriever_hop}"
                / f"k_{k}/test.json"
            )
        )
        predictor_config = srsly.read_yaml(KBQA_PROMPT_CONFIGS_DIR / "gpt_config_knowledge.yaml")
        iterator = zip(df.itertuples(), subgraphs)
    elif predictor_mode == "noknowledge":
        predictor_config = srsly.read_yaml(KBQA_PROMPT_CONFIGS_DIR / "gpt_config_noknowledge.yaml")
        iterator = df.itertuples()
    else:
        raise ValueError(f"Unknown predictor mode: {predictor_mode}")

    client = GPTClient([], predictor_config["final_message_schema"], model)

    output = []
    for i, x in tqdm(enumerate(iterator), total=len(df)):
        if predictor_mode == "knowledge":
            example, subgraph = x
            assert subgraph["example_id"] == example.id
            res = client.get_response(triples=subgraph["subgraph_str"], question=example.question)
        elif predictor_mode == "noknowledge":
            example = x
            res = client.get_response(question=example.question)
        output.append({"example_id": example.id, "response": res})

    with open(output_path / "test.json", "w") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    config = {
        "dataset_name": dataset_name,
        "predictor_mode": predictor_mode,
        "model": model,
        "graph_hop": graph_hop,
        "retriever_hop": retriever_hop,
        "k": k,
    }
    with open(output_path / "config.json", "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


typer.run(main)
