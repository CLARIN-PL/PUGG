import argparse

from beir.datasets.data_loader import GenericDataLoader
from beir.reranking import Rerank
from beir.retrieval import models
from beir.retrieval.evaluation import EvaluateRetrieval
from beir.retrieval.search.dense import DenseRetrievalExactSearch as DRES
from sentence_transformers import CrossEncoder

from gqqd.defaults import IR_RESULTS_PATH


def eval_cross_encoder(
    data_path: str = "data/datasets/final/ir",
    retriever_model_name: str = "intfloat/multilingual-e5-large",
    reranker_model_name: str = "sdadas/polish-reranker-large-ranknet",
    batch_size: int = 32,
    corpus_file: str = "corpus.jsonl",
    query_prefix: str = "query: ",
    passage_prefix: str = "passage: ",
):
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path, corpus_file=corpus_file).load(
        split="test"
    )

    # Add query and passage prefixes
    for key, value in queries.items():
        queries[key] = query_prefix + value

    for key, value in corpus.items():
        corpus[key]["text"] = passage_prefix + value["text"]

    model = DRES(
        models.SentenceBERT(retriever_model_name),
        batch_size=batch_size,
        corpus_chunk_size=512 * 9999,
    )
    retriever = EvaluateRetrieval(model, score_function="cos_sim")

    results = retriever.retrieve(corpus, queries)

    reranked = dict()

    cross_encoder_model = CrossEncoder(reranker_model_name, max_length=512)
    reranker = Rerank(cross_encoder_model, batch_size=batch_size)
    rerank_results = reranker.rerank(corpus, queries, results, top_k=100)

    ndcg, _map, recall, precision = EvaluateRetrieval.evaluate(
        qrels, rerank_results, retriever.k_values
    )

    mrr = EvaluateRetrieval.evaluate_custom(qrels, reranked, retriever.k_values, "mrr")

    print(f"NDCG: {ndcg}")
    print(f"Recall: {recall}")
    print(f"MRR: {mrr}")

    results_name_part1 = retriever_model_name.split("/")[-1]
    results_name_part2 = reranker_model_name.split("/")[-1]
    with open(
        IR_RESULTS_PATH / f"Dense_retriever_{results_name_part1}_reranker_{results_name_part2}", "w"
    ) as f:
        f.write(f"NDCG: {ndcg}\n")
        f.write(f"Recall: {recall}\n")
        f.write(f"MRR: {mrr}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Cross encoder Evaluation", description="Evaluates cross encoder on IR dataset"
    )
    parser.add_argument("--data_path", type=str, default="data/datasets/final/ir", required=False)
    parser.add_argument(
        "--retriever_model_name", type=str, default="intfloat/multilingual-e5-large", required=False
    )
    parser.add_argument(
        "--reranker_model_name",
        type=str,
        default="sdadas/polish-reranker-large-ranknet",
        required=False,
    )
    parser.add_argument("--corpus_file", type=str, default="corpus.jsonl", required=False)
    parser.add_argument("--batch_size", type=int, default=32, required=False)
    parser.add_argument("--query_prefix", type=str, default="query: ", required=False)
    parser.add_argument("--passage_prefix", type=str, default="passage: ", required=False)

    args = parser.parse_args()

    eval_cross_encoder(
        data_path=args.data_path,
        retriever_model_name=args.retriever_model_name,
        reranker_model_name=args.reranker_model_name,
        corpus_file=args.corpus_file,
        batch_size=args.batch_size,
        query_prefix=args.query_prefix,
        passage_prefix=args.passage_prefix,
    )
