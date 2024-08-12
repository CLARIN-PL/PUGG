import json
from collections import defaultdict

import tqdm

from gqqd.defaults import FINAL_DATASET_IR, IR_DATASET_PATH

FULL_CORPUS_PATH = IR_DATASET_PATH / "corpus_full.jsonl"
overlapping_keys_dict = defaultdict(list)

full_corpus = []
with open(FULL_CORPUS_PATH, "r") as f:
    for line in f:
        full_corpus.append(json.loads(line))


pos_corpus_keys = [
    (entry["_id"], entry["text"]) for entry in full_corpus if "neg" not in entry["_id"]
]
neg_corpus_keys = [(entry["_id"], entry["text"]) for entry in full_corpus if "neg" in entry["_id"]]


for pos_key, pos_val in tqdm.tqdm(pos_corpus_keys):
    front = pos_val[:100]
    back = pos_val[-100:]

    for key, val in neg_corpus_keys:
        if front in val:
            overlapping_keys_dict[pos_key].append(key)
        if back in val:
            overlapping_keys_dict[pos_key].append(key)


overlapping_keys_set = set()
for key_list in overlapping_keys_dict.values():
    for item in key_list:
        overlapping_keys_set.add(item)


filtered_corpus = [entry for entry in full_corpus if entry["_id"] not in overlapping_keys_set]


with open(FINAL_DATASET_IR / "corpus.jsonl", "w") as f:
    for entry in filtered_corpus:
        f.write(json.dumps(entry, ensure_ascii=False))
        f.write("\n")
