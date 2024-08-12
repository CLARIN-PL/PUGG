import json
import os

import datasets

logger = datasets.logging.get_logger(__name__)

_CORPUS = "corpus"
_QUERIES = "queries"
_QRELS = "qrels"

URL = ""
_URLs = {
    _CORPUS: f"corpus.jsonl",
    _QUERIES: f"queries.jsonl",
    _QRELS: f"qrels/test.tsv",
}


class PuggIr(datasets.GeneratorBasedBuilder):

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name=_CORPUS,
        ),
        datasets.BuilderConfig(
            name=_QUERIES,
        ),
        datasets.BuilderConfig(
            name=_QRELS,
        ),
    ]

    def _info(self):
        if self.config.name == _CORPUS:
            features = datasets.Features(
                {
                    "_id": datasets.Value("string"),
                    "title": datasets.Value("string"),
                    "text": datasets.Value("string"),
                }
            )
        elif self.config.name == _QUERIES:
            features = datasets.Features(
                {
                    "_id": datasets.Value("string"),
                    "query": datasets.Value("string"),
                }
            )
        elif self.config.name == _QRELS:
            features = datasets.Features(
                {
                    "query-id": datasets.Value("string"),
                    "corpus-id": datasets.Value("string"),
                    "score": datasets.Value("int32"),
                }
            )

        return datasets.DatasetInfo(
            features=features,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        my_urls = _URLs[self.config.name]
        data_dir = dl_manager.download_and_extract(my_urls)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": data_dir},
            ),
        ]

    def _generate_examples(self, filepath):
        """Yields examples."""
        if self.config.name in [_CORPUS, _QUERIES]:
            with open(filepath, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    data = json.loads(line)
                    yield i, data

        elif self.config.name == _QRELS:
            with open(filepath, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == 0:
                        continue  # Skip header
                    query_id, corpus_id, score = line.strip().split("\t")
                    yield i, {
                        "query-id": query_id,
                        "corpus-id": corpus_id,
                        "score": int(score),
                    }
