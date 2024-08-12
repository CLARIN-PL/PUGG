import argparse

from beir.datasets.data_loader import GenericDataLoader
from beir.reranking import Rerank
from beir.reranking.models import MonoT5
from beir.retrieval.evaluation import EvaluateRetrieval
from src.bm25_search_beir_patch import BM25Search as BM25

from gqqd.defaults import IR_RESULTS_PATH


def eval_t5_reranker(
    data_path: str = "data/datasets/ir_dataset",
    index_name: str = "ir_dataset",
    model_name: str = "clarin-knext/plt5-large-msmarco",
    batch_size: int = 64,
    corpus_file: str = "corpus.jsonl",
    hostname: str = "localhost",
    initialize: bool = True,
):
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path, corpus_file=corpus_file).load(
        split="test"
    )

    number_of_shards = 1
    model = BM25(
        index_name=index_name,
        hostname=hostname,
        initialize=initialize,
        number_of_shards=number_of_shards,
        language="polish",
    )

    retriever = EvaluateRetrieval(model)

    results = retriever.retrieve(corpus, queries)

    reranked = dict()

    # Tokens might be different for different models
    cross_encoder_model = MonoT5(
        model_name, use_amp=False, token_false="▁fałsz", token_true="▁prawda"
    )
    reranker = Rerank(cross_encoder_model, batch_size=batch_size)

    # Rerank top-100 results using the reranker provided
    rerank_results = reranker.rerank(corpus, queries, results, top_k=100)

    ndcg, _map, recall, precision = EvaluateRetrieval.evaluate(
        qrels, rerank_results, retriever.k_values
    )

    mrr = retriever.evaluate_custom(qrels, reranked, retriever.k_values, "mrr")

    print(f"NDCG: {ndcg}")
    print(f"Recall: {recall}")
    print(f"MRR: {mrr}")

    results_name = model_name.split("/")[-1]
    with open(IR_RESULTS_PATH / f"BM25_monot5_{results_name}", "w") as f:
        f.write(f"Model name: {model_name}\n")
        f.write(f"NDCG: {ndcg}\n")
        f.write(f"Recall: {recall}\n")
        f.write(f"MRR: {mrr}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="MonoT5 with BM25 evaluation", description="Evaluates MonoT5 on IR dataset"
    )
    parser.add_argument("--data_path", type=str, default="data/datasets/ir_dataset", required=False)
    parser.add_argument(
        "--model_name", type=str, default="clarin-knext/plt5-large-msmarco", required=False
    )
    parser.add_argument("--corpus_file", type=str, default="corpus_full.jsonl", required=False)
    parser.add_argument("--batch_size", type=int, default=64, required=False)
    parser.add_argument("--hostname", type=str, default="localhost", required=False)
    parser.add_argument("--initialize", default=False, action="store_true")
    parser.add_argument("--index_name", type=str, default="ir_dataset_full", required=False)

    args = parser.parse_args()

    eval_t5_reranker(
        data_path=args.data_path,
        model_name=args.model_name,
        corpus_file=args.corpus_file,
        batch_size=args.batch_size,
        hostname=args.hostname,
        initialize=args.initialize,
        index_name=args.index_name,
    )
