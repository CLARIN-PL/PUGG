import json

import srsly
from sklearn.model_selection import train_test_split

from gqqd.defaults import FINAL_DATASET_KBQA, FINAL_GQQD_DATASET

TEST_SIZE = 0.2

dataset = srsly.read_json(FINAL_GQQD_DATASET / "kbqa_labeled.json")
for entry in dataset:
    entry["topic"] = [entity["entity_id"] for entity in entry["topic"]]
    entry["answer"] = [entity["entity_id"] for entity in entry["answer"]]
train, test = train_test_split(dataset, test_size=TEST_SIZE, shuffle=False)
(output_dir := FINAL_DATASET_KBQA / "kbqa_natural").mkdir(exist_ok=True, parents=True)
with open(output_dir / "train.json", "w") as f:
    json.dump(train, f, indent=4, ensure_ascii=False)
with open(output_dir / "test.json", "w") as f:
    json.dump(test, f, indent=4, ensure_ascii=False)
