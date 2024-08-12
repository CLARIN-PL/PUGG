import argparse
import logging

from beir import LoggingHandler
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.evaluation import EvaluateRetrieval
from src.bm25_search_beir_patch import BM25Search as BM25

from gqqd.defaults import IR_RESULTS_PATH


def eval_bm25(
    data_path: str = "data/datasets/ir_dataset",
    index_name: str = "ir_dataset",
    corpus_file: str = "corpus.jsonl",
    hostname: str = "localhost",
    initialize: bool = True,
):
    #### Just some code to print debug information to stdout
    logging.basicConfig(
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        handlers=[LoggingHandler()],
    )

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

    logging.info("Retriever evaluation for k in: {}".format(retriever.k_values))
    ndcg, _map, recall, precision = retriever.evaluate(qrels, results, retriever.k_values)

    mrr = retriever.evaluate_custom(qrels, results, retriever.k_values, "mrr")

    print(f"NDCG: {ndcg}")
    print(f"Recall: {recall}")
    print(f"MRR: {mrr}")

    with open(IR_RESULTS_PATH / "BM25_morfologik", "w") as f:
        f.write("Model name: BM25\n")
        f.write(f"NDCG: {ndcg}\n")
        f.write(f"Recall: {recall}\n")
        f.write(f"MRR: {mrr}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="BM25 Evaluation", description="Evaluates BM25 on IR dataset"
    )
    parser.add_argument("--data_path", type=str, default="data/datasets/final/ir", required=False)
    parser.add_argument("--index_name", type=str, default="ir_dataset", required=False)
    parser.add_argument("--corpus_file", type=str, default="corpus.jsonl", required=False)
    parser.add_argument("--hostname", type=str, default="localhost", required=False)
    parser.add_argument("--initialize", default=False, action="store_true")

    args = parser.parse_args()

    eval_bm25(
        data_path=args.data_path,
        index_name=args.index_name,
        corpus_file=args.corpus_file,
        hostname=args.hostname,
        initialize=args.initialize,
    )
