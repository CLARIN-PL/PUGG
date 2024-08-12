import json
from dataclasses import asdict
from random import Random

import srsly
from sklearn.model_selection import train_test_split

from gqqd.defaults import FINAL_DATASET_KBQA
from gqqd.pipeline.output.data import KBQAEntity
from sqqd.defaults import OUTPUT_PATH
from sqqd.pipeline.data import KBQATemplateBasedExample

TEST_SIZE = 0.2

input_data_path = OUTPUT_PATH / "results_db_filtered.json"
input_data = srsly.read_json(input_data_path)
output_data = []
i = 0
Random(17).shuffle(input_data)
for example in input_data:
    topic = [
        KBQAEntity(entry_id, entry_label)
        for entry_id, entry_label in zip(
            example["question_entity_ids"], example["question_entity_labels"]
        )
    ]
    answer = [
        KBQAEntity(entry_id, entry_label)
        for entry_id, entry_label in zip(example["answer_ids"], example["answer_labels"])
    ]
    final_example = KBQATemplateBasedExample(
        id=f"kbqa_template_based_{i}",
        question=example["paraphrased_question"],
        topic=topic,
        answer=answer,
        sparql_query=example["sparql_query"],
        sparql_query_template=example["template"],
    )
    output_data.append(asdict(final_example))
    i += 1

for entry in output_data:
    entry["topic"] = [entity["entity_id"] for entity in entry["topic"]]
    entry["answer"] = [entity["entity_id"] for entity in entry["answer"]]
train, test = train_test_split(output_data, test_size=TEST_SIZE, shuffle=False)
(output_dir := FINAL_DATASET_KBQA / "kbqa_template-based").mkdir(exist_ok=True, parents=True)
with open(output_dir / "train.json", "w") as f:
    json.dump(train, f, indent=4, ensure_ascii=False)
with open(output_dir / "test.json", "w") as f:
    json.dump(test, f, indent=4, ensure_ascii=False)
