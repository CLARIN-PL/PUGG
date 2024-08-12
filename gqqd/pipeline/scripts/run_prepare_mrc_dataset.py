import json
import os

from sklearn.model_selection import train_test_split

from gqqd.data.deduplicator import MRCDeduplicator
from gqqd.data.inforex import load_inforex_output_df
from gqqd.data.postprocessor import QuestionPostprocessor
from gqqd.defaults import ANNOTATED_PATH, FINAL_DATASET_MRC, MRC_DATASET_PATH

# Load final inforex export
INFOREX_EXPORT_PATH = ANNOTATED_PATH / "inforex/inforex_export_904"
INFOREX_ITERATION_ZERO_PATH = ANNOTATED_PATH / "inforex_input_iteration_0.json"

deduplicator = MRCDeduplicator()
qa_postprocessor = QuestionPostprocessor()

all_data = load_inforex_output_df(INFOREX_EXPORT_PATH)

text_docs = [
    entry.name
    for entry in os.scandir(INFOREX_EXPORT_PATH / "documents")
    if entry.name.endswith(".txt")
]


with open(INFOREX_ITERATION_ZERO_PATH, "r") as f:
    inforex_iteration_zero = json.load(f)

docs_dict = {}
for text_file in text_docs:
    with open(INFOREX_EXPORT_PATH / "documents" / text_file) as f:
        text = f.read()
    doc_id = text_file.split(".")[0]
    entry = all_data.loc[all_data["report_id"] == str(int(doc_id))]

    annotation = entry["human_annotation"].values[0].strip()
    start_idx = text.find(annotation)
    end_idx = start_idx + len(annotation)
    annotation_id = int(entry["id"])
    q_p_id = entry["q_p_id"].values[0]

    # Check if duplicate
    if deduplicator.is_duplicate(q_p_id):
        continue
    docs_dict[doc_id] = {
        "context": text,
        "answer": annotation,
        "start_idx": start_idx,
        "end_idx": end_idx,
        "annotation_id": annotation_id,
        "q_p_id": q_p_id,
    }


for doc_idx, doc_annotations in docs_dict.items():
    q_p_id = doc_annotations["q_p_id"]
    for iter_zero_entry in inforex_iteration_zero:
        if iter_zero_entry["q_p_id"] == q_p_id:
            doc_annotations["question"] = qa_postprocessor(iter_zero_entry["question"])
            break


qa_dataset_list = []
for num, (doc_id, doc_annotation) in enumerate(docs_dict.items()):
    doc_annotation["id"] = f"mrc_{num}"
    qa_dataset_list.append(doc_annotation)


qa_dataset_train, qa_dataset_test = train_test_split(
    qa_dataset_list, test_size=0.2, random_state=42
)

with open(MRC_DATASET_PATH / "mrc_dataset.json", "w") as f:
    json.dump(qa_dataset_list, f, ensure_ascii=False)


final_mrc_train = []
for num, entry in enumerate(qa_dataset_train):
    question = entry["question"]
    answer = entry["answer"]
    context = entry["context"]
    start_idx = entry["start_idx"]
    end_idx = entry["end_idx"]
    _id = f"mrc_{num}"
    final_mrc_train.append(
        {
            "id": _id,
            "question": question,
            "answer": answer,
            "context": context,
            "start_idx": start_idx,
            "end_idx": end_idx,
        }
    )

test_start_idx = len(final_mrc_train)

final_mrc_test = []
for num, entry in enumerate(qa_dataset_test, start=test_start_idx):
    question = entry["question"]
    answer = entry["answer"]
    context = entry["context"]
    start_idx = entry["start_idx"]
    end_idx = entry["end_idx"]
    _id = f"mrc_{num}"
    final_mrc_test.append(
        {
            "id": _id,
            "question": question,
            "answer": answer,
            "context": context,
            "start_idx": start_idx,
            "end_idx": end_idx,
        }
    )


# Here save final MRC dataset splits
with open(FINAL_DATASET_MRC / "train.json", "w") as f:
    json.dump(final_mrc_train, f, ensure_ascii=False)

with open(FINAL_DATASET_MRC / "test.json", "w") as f:
    json.dump(final_mrc_test, f, ensure_ascii=False)
