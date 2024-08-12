import pickle
from pathlib import Path

import numpy as np
import srsly
import torch
from sentence_transformers import SentenceTransformer

from baselines.defaults import KBQA_EMBEDDINGS_PATH
from baselines.kbqa.data import load_graph
from gqqd.defaults import FINAL_DATASET_KBQA

EMBEDDING_MODEL = "sdadas/mmlw-retrieval-roberta-large"
QUERY_PREFIX = "zapytanie: "


def question_embeddings(output_path: Path):
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")

    for dataset in ["kbqa_template-based", "kbqa_natural"]:
        for split in ["train", "test"]:
            dataset = srsly.read_json(FINAL_DATASET_KBQA / dataset / f"{split}.json")
            queries = [QUERY_PREFIX + example["question"] for example in dataset]
            queries_emb = model.encode(queries, convert_to_tensor=True, show_progress_bar=True)
            assert queries_emb.shape[0] == len(queries)
            torch.save(queries_emb, output_path / f"emb_{dataset}_{split}.pt")


def triples_embeddings(output_path: Path):
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")

    for hop in reversed([1, 2]):
        print(f"Embedding triples - {hop} hop...")
        triples, labels = load_graph(hop)
        triples = np.array(triples)
        triples_string = np.array(
            [f"{labels.get(s)}, {labels.get(p)}, {labels.get(o)}" for s, p, o in triples]
        )
        pool = model.start_multi_process_pool()
        emb = model.encode_multi_process(triples_string, pool)
        model.stop_multi_process_pool(pool)
        torch.save(
            emb, output_path / f"emb_triples_hop_{hop}.pt", pickle_protocol=pickle.HIGHEST_PROTOCOL
        )
        del emb


if __name__ == "__main__":
    KBQA_EMBEDDINGS_PATH.mkdir(exist_ok=True, parents=True)
    question_embeddings(KBQA_EMBEDDINGS_PATH)
    triples_embeddings(KBQA_EMBEDDINGS_PATH)
