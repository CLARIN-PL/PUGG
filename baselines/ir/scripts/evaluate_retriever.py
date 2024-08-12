import argparse
import logging
from time import time

from beir import LoggingHandler
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval import models
from beir.retrieval.evaluation import EvaluateRetrieval
from beir.retrieval.search.dense import DenseRetrievalExactSearch as DRES

from gqqd.defaults import IR_RESULTS_PATH


def eval_biencoder(
    data_path: str = "data/datasets/final/ir",
    corpus_file: str = "corpus.jsonl",
    model_name: str = "intfloat/multilingual-e5-base",
    batch_size: int = 64,
    query_prefix: str = "query: ",
    passage_prefix: str = "passage: ",
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

    # Add query and passage prefixes
    for key, value in queries.items():
        queries[key] = query_prefix + value

    for key, value in corpus.items():
        corpus[key]["text"] = passage_prefix + value["text"]

    #### Dense Retrieval using SBERT (Sentence-BERT) ####
    #### Provide any pretrained sentence-transformers model
    #### The model was fine-tuned using cosine-similarity.
    #### Complete list - https://www.sbert.net/docs/pretrained_models.html

    model = DRES(
        models.SentenceBERT(model_name), batch_size=batch_size, corpus_chunk_size=512 * 9999
    )
    retriever = EvaluateRetrieval(model, score_function="cos_sim")

    #### Retrieve dense results (format of results is identical to qrels)
    start_time = time()
    results = retriever.retrieve(corpus, queries)
    end_time = time()
    print("Time taken to retrieve: {:.2f} seconds".format(end_time - start_time))
    #### Evaluate your retrieval using NDCG@k, MAP@K ...

    logging.info("Retriever evaluation for k in: {}".format(retriever.k_values))
    ndcg, _map, recall, precision = retriever.evaluate(qrels, results, retriever.k_values)
    mrr = retriever.evaluate_custom(qrels, results, retriever.k_values, metric="mrr")

    print(f"NDCG: {ndcg}")
    print(f"Recall: {recall}")
    print(f"MRR: {mrr}")

    results_name = model_name.split("/")[-1]
    with open(IR_RESULTS_PATH / f"retriever_{results_name}", "w") as f:
        f.write(f"Model name: {model_name}\n")
        f.write(f"NDCG: {ndcg}\n")
        f.write(f"Recall: {recall}\n")
        f.write(f"MRR: {mrr}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Retriever Evaluation", description="Evaluates retriever on IR dataset"
    )
    parser.add_argument("--data_path", type=str, default="data/datasets/final/ir", required=False)
    parser.add_argument(
        "--model_name", type=str, default="intfloat/multilingual-e5-base", required=False
    )
    parser.add_argument("--corpus_file", type=str, default="corpus.jsonl", required=False)
    parser.add_argument("--batch_size", type=int, default=64, required=False)

    parser.add_argument("--query_prefix", type=str, default="zapytanie: ", required=False)
    parser.add_argument("--passage_prefix", type=str, default="", required=False)

    args = parser.parse_args()

    eval_biencoder(
        data_path=args.data_path,
        model_name=args.model_name,
        corpus_file=args.corpus_file,
        batch_size=args.batch_size,
        query_prefix=args.query_prefix,
        passage_prefix=args.passage_prefix,
    )
