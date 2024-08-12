import json
from pathlib import Path

import pandas as pd
import srsly

from gqqd.data.inforex import load_inforex_output_df
from gqqd.defaults import ANNOTATED_PATH, IR_DATASET_PATH, OUTPUT_PATH

gpt_annotated_path = Path(ANNOTATED_PATH / "gpt_auto_annotated_iteration_0.json")
inforex_input_path = Path(ANNOTATED_PATH / "inforex_input_iteration_0.json")
inforex_output_id = 904
inforex_output_path = Path(ANNOTATED_PATH / f"inforex/inforex_export_{inforex_output_id}")

inforex_input_df = pd.read_json(inforex_input_path)
inforex_output_df = load_inforex_output_df(inforex_output_path)

gpt_annotated_df = pd.read_json(gpt_annotated_path)
gpt_annotated_df.rename(columns={"id": "q_id"}, inplace=True)

correct_q_p_id_set = set(inforex_output_df.q_p_id)
correct_q_id_set = set(inforex_input_df[inforex_input_df.q_p_id.isin(correct_q_p_id_set)].q_id)
correct_gpt_annotation = gpt_annotated_df[gpt_annotated_df.q_id.isin(correct_q_id_set)].reset_index(
    drop=True
)

correct_gpt_annotation["q_p_id"] = correct_gpt_annotation.q_id.map(
    dict(zip(inforex_input_df.q_id, inforex_input_df.q_p_id))
)
correct_gpt_annotation["p_id"] = correct_gpt_annotation.q_p_id.map(
    dict(zip(inforex_input_df.q_p_id, inforex_input_df.p_id))
)

df = correct_gpt_annotation.reset_index(drop=True)
df = pd.concat([df, pd.json_normalize(df.passage)], axis=1)
df = df.drop(columns=["passage"])

for entry in df.itertuples():
    assert entry.text[entry.span[0] : entry.span[1]] == entry.gpt_answer

data = srsly.read_json(OUTPUT_PATH / "qa_for_annotation.json")
passages = {passage["text"] for entry in data for passage in entry["passages"]}
print(len(passages))
assert df.text.isin(passages).mean() == 1.0


with open(IR_DATASET_PATH / "all_passages.jsonl", "w") as f:
    for num, passage in enumerate(passages):
        f.write(json.dumps({"text": passage, "_id": "passage_{}".format(num)}, ensure_ascii=False))
        f.write("\n")
