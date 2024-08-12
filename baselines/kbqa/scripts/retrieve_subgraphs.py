import json
import time
from itertools import chain

import mpire
import numpy as np
import pandas as pd
import torch
import typer
from tqdm import tqdm

from baselines.defaults import KBQA_BASELINES_PATH
from baselines.kbqa.data import load_dataset, load_graph
from baselines.kbqa.subgraph_retriever import FilteredTriplesNHopRetriever


def main(
    dataset_name: str = typer.Option(...),
    subset: str = typer.Option(...),
    graph_hop: int = typer.Option(...),
    retriever_hop: int = typer.Option(...),
    k: int = typer.Option(...),
    workers: int = typer.Option(...),
) -> None:
    output_path = (
        KBQA_BASELINES_PATH
        / "subgraphs"
        / f"graph_hop_{graph_hop}"
        / dataset_name
        / f"retriever_hop_{retriever_hop}"
        / f"k_{k}"
    )
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Retrieving for {dataset_name}...")
    print("Loading dataset and graph...")
    dataset = load_dataset(dataset_name)[subset]
    df = pd.DataFrame(dataset)
    chunks = np.array_split(df, workers)
    print("Retrieving subgraphs...")
    with mpire.WorkerPool(workers, pass_worker_id=True) as pool:
        results = pool.map(
            retrieve_for_chunk,
            [(chunk, graph_hop, dataset_name, retriever_hop, k, subset) for chunk in chunks],
        )

    output = list(chain.from_iterable(results))

    with open(output_path / f"{subset}.json", "w") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)


def retrieve_for_chunk(
    worker_id,
    chunk: pd.DataFrame,
    graph_hop: int,
    dataset_name: str,
    retriever_hop: int,
    k: int,
    subset: str,
) -> list[dict[str, str]]:
    time.sleep(worker_id * 15)
    triples, labels = load_graph(graph_hop)
    triples = np.array(triples)
    print(f"{worker_id}: Loading tensors...")
    triples_emb = torch.load(
        KBQA_BASELINES_PATH / f"embeddings/emb_triples_hop_{graph_hop}.pt",
        map_location=torch.device("cpu"),
    )
    queries_emb = torch.load(
        KBQA_BASELINES_PATH / f"embeddings/emb_{dataset_name}_{subset}.pt",
        map_location=torch.device("cpu"),
    )
    print(f"{worker_id}: Initializing predictor...")
    retriever = FilteredTriplesNHopRetriever(
        retriever_hop, triples, labels=labels, triples_emb=triples_emb
    )
    output = []
    for i, example in tqdm(enumerate(chunk.itertuples()), total=len(chunk), desc=f"{worker_id}"):
        print(f"{worker_id}:{i}/{len(chunk)}")
        topic = example.topic
        subgraph = retriever.retrieve(topic, query_emb=queries_emb[example.Index], k_triples=k)
        subgraph_str = ", ".join(
            f'("{labels.get(h, h)}", "{labels.get(r, r)}", "{labels.get(t, t)}")'
            for h, r, t in subgraph
        )
        output.append({"example_id": example.id, "subgraph_str": subgraph_str})
    return output


typer.run(main)
