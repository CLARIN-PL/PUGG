import csv
import json
import os
from collections import defaultdict

import tqdm

from gqqd.defaults import FINAL_DATASET_IR, IR_DATASET_PATH, MRC_DATASET_PATH

# HERE LOAD QA DATASET
with open(MRC_DATASET_PATH / "mrc_dataset.json", "r") as f:
    mrc_dataset = json.load(f)

# Dataset format examples
corpus, queries, q_rels = [], [], []
corpus_dict_example = {"_id": "0", "title": "", "text": "", "metadata": {}}
query_dict_example = {"_id": "0", "text": "", "metadata": {}}


for num, entry in tqdm.tqdm(enumerate(mrc_dataset)):
    context = entry["context"]
    query = entry["question"]
    corpus.append({"_id": f"doc_{num}", "title": "", "text": context, "metadata": {}})
    queries.append({"_id": f"query_{num}", "text": query, "metadata": {}})
    q_rels.append([f"query_{num}", f"doc_{num}"])


text_set = {entry["text"] for entry in corpus}
queries_set = {entry["text"] for entry in queries}

# Find duplicate indices
indices = defaultdict(list)
for i, entry in enumerate(corpus):
    indices[entry["text"]].append(i)


corpus_indeces_to_remove = []
for k, v in indices.items():
    if len(v) > 1:
        for index in v[1:]:
            q_rels[index][1] = q_rels[v[0]][1]
            corpus_indeces_to_remove.append(index)

corpus_indeces_to_remove = set(corpus_indeces_to_remove)

corpus = [entry for i, entry in enumerate(corpus) if i not in corpus_indeces_to_remove]

# Save small corpus of the IR Dataset, this corpus contains only relevant passages.

with open(IR_DATASET_PATH / "corpus_small.jsonl", "w") as f:
    for entry in corpus:
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")

with open(FINAL_DATASET_IR / "queries.jsonl", "w") as f:
    for entry in queries:
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")

QRELS_PATH = FINAL_DATASET_IR / "qrels"
if not os.path.exists(QRELS_PATH):
    os.makedirs(QRELS_PATH)

with open(QRELS_PATH / "test.tsv", "w") as f:
    csv_writer = csv.writer(f, delimiter="\t")
    csv_writer.writerow(["query-id", "corpus-id", "score"])
    for query_id, corpus_id in q_rels:
        csv_writer.writerow([query_id, corpus_id, 1])


# Load all passages
all_passages = []
with open(IR_DATASET_PATH / "all_passages.jsonl", "r") as f:
    for line in f:
        all_passages.append(json.loads(line))


# Filtering all passages
corpus_text_set = {entry["text"] for entry in corpus}
num = 0
for neg_passage in all_passages:
    if neg_passage["text"] in corpus_text_set:
        continue
    else:
        corpus.append(
            {"_id": f"neg_doc_{num}", "title": "", "text": neg_passage["text"], "metadata": {}}
        )
        num += 1


with open(IR_DATASET_PATH / "corpus_full.jsonl", "w") as f:
    for entry in corpus:
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")
