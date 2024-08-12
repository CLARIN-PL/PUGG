from itertools import chain
from statistics import mean
from typing import Any

import pandas as pd
import srsly

from baselines.defaults import KBQA_BASELINES_PATH, KBQA_RESULTS_PATH, ROOT_PATH
from baselines.kbqa.data import load_dataset, load_graph


def main() -> None:
    _, labels = load_graph(0)

    results = []

    for config in load_configs():
        entry = (
            KBQA_BASELINES_PATH
            / "predictions"
            / config["predictor_mode"]
            / f"graph_hop_{config.get('graph_hop', None)}"
            / config["model"]
            / config["dataset_name"]
            / f"retriever_hop_{config.get('retriever_hop', None)}"
            / f"k_{config.get('k', None)}"
            / "test.json"
        )
        responses = srsly.read_json(entry)
        dataset = load_dataset(config["dataset_name"])["test"]
        results.append({**config, "accuracy": evaluate(dataset, responses, labels)})

    results_df = pd.DataFrame(results)
    results_df = results_df.explode("accuracy")

    single_dataset = (
        results_df.groupby(
            ["dataset_name", "predictor_mode", "model", "graph_hop", "retriever_hop", "k"],
            dropna=False,
        )
        .accuracy.mean()
        .reset_index()
    )
    single_dataset = single_dataset.sort_values(
        ["dataset_name", "predictor_mode"], ascending=[True, False]
    )
    single_dataset = single_dataset.drop(columns=["model", "k"])
    single_dataset.accuracy = single_dataset.accuracy.round(3)

    all_datasets = (
        results_df.groupby(
            ["predictor_mode", "model", "graph_hop", "retriever_hop", "k"], dropna=False
        )
        .accuracy.mean()
        .reset_index()
    )
    all_datasets["dataset_name"] = "KBQA (all"
    all_datasets = all_datasets.sort_values(
        ["dataset_name", "predictor_mode"], ascending=[True, False]
    )
    all_datasets = all_datasets.drop(columns=["model", "k"])
    all_datasets.accuracy = all_datasets.accuracy.round(3)

    final = pd.concat([single_dataset, all_datasets])
    final.dataset_name = final.dataset_name.str.replace("_", " (")
    final.dataset_name = final.dataset_name.str.replace("kbqa", "KBQA")
    final.dataset_name = final.dataset_name + ")"
    final.predictor_mode = final.predictor_mode.str.replace("noknowledge", "w/o KG")
    final.predictor_mode = final.predictor_mode.str.replace("knowledge", "w/ KG")

    latex_table = final.to_latex(index=False)
    print(latex_table)
    output_path = KBQA_RESULTS_PATH / "final_results.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(latex_table)


def load_configs():
    stages = srsly.read_yaml(ROOT_PATH / "dvc.yaml")["stages"]
    configs = list(
        chain.from_iterable(
            stages[stage]["foreach"]
            for stage in ["baseline_kbqa_predict_knowledge", "baseline_kbqa_predict_noknowledge"]
        )
    )
    return configs


def evaluate(
    dataset: list[dict[str, Any]], responses: list[dict[str, str]], labels: dict[str, str]
) -> list[float]:
    accs = []
    for example, res in zip(dataset, responses):
        assert example["id"] == res["example_id"]
        answer = [labels[x] for x in example["answer"]]
        answer = [x.lower() for x in answer]
        generated_answer = res["response"][0].lower()
        acc = mean(1.0 if entity in generated_answer else 0.0 for entity in answer)
        accs.append(acc)
    return accs


main()
