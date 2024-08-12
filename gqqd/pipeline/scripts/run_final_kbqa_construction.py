import json
from dataclasses import asdict
from urllib.parse import unquote

import numpy as np
import pandas as pd
from mpire import WorkerPool
from tinydb import TinyDB

from gqqd.api.wikidata import WikidataClient
from gqqd.data.deduplicator import MRCDeduplicator
from gqqd.data.final import get_final_df
from gqqd.data.postprocessor import QuestionPostprocessor
from gqqd.defaults import ENTITY_LINKING_ANNOTATION, ENTITY_LINKING_OUTPUT, FINAL_GQQD_DATASET
from gqqd.pipeline.output.data import KBQAEntity, KBQANaturalExample

np.random.seed(17)


def main() -> None:
    data = load_positively_verified()
    manually_corrected_topics, discard = load_manually_corrected_topics()
    positive_entities = data.groupby("q_p_id")["entity_id"].apply(list).to_dict()
    for k, v in manually_corrected_topics.items():
        positive_entities[k] = v

    el_output = []
    for iter_num in [0, 1]:
        el_output.extend(
            TinyDB(ENTITY_LINKING_OUTPUT / f"{iter_num}/output.json").table("results").all()
        )

    deduplicator = MRCDeduplicator()
    postprocessor = QuestionPostprocessor()
    final = []
    for entry in el_output:
        if entry["q_p_id"] not in positive_entities or entry["q_p_id"] in discard:
            continue
        if deduplicator.is_duplicate(entry["q_p_id"]):
            continue
        answer = [
            KBQAEntity(entity_id=entity_id, entity_label="unknown")
            for label, entity_id in zip(entry["answer_entities"], entry["answer_entities_ids"])
            if entity_id is not None
        ]
        if len(answer) == 0:
            continue

        topic = [
            KBQAEntity(entity_id=entity_id, entity_label="unknown")
            for entity_id in positive_entities[entry["q_p_id"]]
        ]
        question = postprocessor(entry["question"])
        example = KBQANaturalExample(
            id=entry["q_p_id"], question=question, answer=answer, topic=topic
        )
        final.append(example)

    print(f"Number of final examples: {len(final)}")
    FINAL_GQQD_DATASET.mkdir(exist_ok=True, parents=True)
    with open(FINAL_GQQD_DATASET / "kbqa_unlabeled.json", "w") as f:
        json.dump([asdict(e) for e in final], f, indent=4, ensure_ascii=False)


def load_positively_verified() -> pd.DataFrame:
    final_df = get_final_df()
    positively_verified = final_df[(final_df.annotation == 1) & (final_df.note == "")].reset_index(
        drop=True
    )

    print(f"Number of input questions: {final_df.q_p_id.nunique()}")
    print(f"Number of positively verified questions: {positively_verified.q_p_id.nunique()}")
    print(f"Number of notes: {final_df[(final_df.note != '')].q_p_id.nunique()}")
    return positively_verified


def load_manually_corrected_topics() -> tuple[dict[str, list[str]], list[str]]:
    df = pd.read_csv(ENTITY_LINKING_ANNOTATION / "correction/corrected.csv")
    discard = df[df.entity_page.isna() | (df.entity_page.str.len() == 0)].q_p_id.tolist()
    df = df[df.entity_page.notna() & (df.entity_page.str.len() > 0)]
    df["entity"] = df.entity_page.apply(lambda x: unquote(x.split("/")[-1])).tolist()
    client = WikidataClient()
    with WorkerPool(5, start_method="threading") as pool:
        df["entity_id"] = pool.map(client.get_wikidata_id, df.entity, progress_bar=True)
    assert df.entity_id.isna().sum() == 0 and df.entity_id.str.startswith("Q").all()
    print(f"Number of manually corrected questions: {len(df)}")
    return df.groupby("q_p_id")["entity_id"].apply(list).to_dict(), discard


main()
