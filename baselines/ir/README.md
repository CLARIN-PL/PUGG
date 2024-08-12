# Information Retrieval dataset

Results can be found under the following path:
`data/baselines/ir`

### BM25 baseline
In order to evaluate BM25 baseline you have to setup local Elasticsearch instance. There is provided docker-compose file used to setup a local instance of Elasticsearch. You will NEED local Elasticsearch instance to reproduce reranker baselines where the retriever is a BM25.

Run:
`sudo docker compose -f baselines/ir/scripts/elasticsearch/docker-compose.yml up`

If you have troubles with some errors, change write and read rights to `esdata` folder. You can also change it's location if needed.


Use the script `evaluate_bm25.py` or run dvc stage `baseline_ir_bm25_evaluate`. 

### Biencoders

Use the script `evaluate_retriever.py` or run dvc stage `baseline_ir_retriever_evaluate`.

Example usage:
```
PYTHONPATH=. python3 baselines/ir/scripts/evaluate_retriever.py
            --model_name ${item.model_path}
            --query_prefix ${item.query_prefix}
            --passage_prefix ${item.passage_prefix}
```

### Rerankers with BM25 retriever

Use the script `evaluate_rerankers.py` or run dvc stage `baseline_ir_bm25_reranker_evaluate`.
Remember that you need local Elasticsearch instance.

Example usage:

```
PYTHONPATH=. python3 baselines/ir/scripts/evaluate_reranker.py
            --model_name ${item.model_path}
```


If you need only positive passages file for evaluation, it is located in: `data/datasets/ir_dataset/corpus_small.jsonl`
