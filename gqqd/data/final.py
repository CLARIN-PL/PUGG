from collections import defaultdict

import numpy as np
import pandas as pd

from gqqd.defaults import ENTITY_LINKING_ANNOTATION


def load_el_ver_output() -> tuple[pd.DataFrame, pd.DataFrame]:
    annotator_0 = pd.concat(
        [
            pd.read_csv(ENTITY_LINKING_ANNOTATION / "output/0/annotator_0.csv"),
            pd.read_csv(ENTITY_LINKING_ANNOTATION / "output/1/annotator_0.csv"),
        ]
    )
    annotator_1 = pd.concat(
        [
            pd.read_csv(ENTITY_LINKING_ANNOTATION / "output/0/annotator_1.csv"),
            pd.read_csv(ENTITY_LINKING_ANNOTATION / "output/1/annotator_1.csv"),
        ]
    )
    df = (
        pd.concat(
            [annotator_0, annotator_1],
            keys=["annotator_0", "annotator_1"],
            names=["annotator", "index"],
        )
        .reset_index()
        .drop(columns="index")
    )

    for col in ["q_p_id", "q_id", "p_id", "question", "answer_entities"]:
        df[col].fillna(method="ffill", inplace=True)

    notes: defaultdict[str, str] = defaultdict(str)
    for entry in df[df.note.notna()].itertuples():
        if entry.note is not None:
            notes[entry.q_p_id] += f"{entry.note};"
    df["note"] = df.q_p_id.map(notes)

    assert df.annotation.nunique() == 2
    common_q_p_id = set(annotator_0.q_p_id.unique()) & set(annotator_1.q_p_id.unique())
    individual_q_p_id = (
        set(annotator_0.q_p_id.unique()) | set(annotator_1.q_p_id.unique())
    ) - common_q_p_id
    individual_df = df[df.q_p_id.isin(individual_q_p_id)].reset_index(drop=True)
    common_df = df[df.q_p_id.isin(common_q_p_id)].reset_index(drop=True)
    return individual_df, common_df


def get_final_df() -> pd.DataFrame:
    individual_df, common_df = load_el_ver_output()
    differences = get_differences_df(common_df)
    final_common = get_final_common_df(common_df, differences)
    final_df = pd.concat([individual_df, final_common], ignore_index=True)
    return final_df


def get_differences_df(common_df: pd.DataFrame) -> pd.DataFrame:
    pivot_data = common_df.pivot(
        index=["q_p_id", "question", "entity_id", "entity"],
        columns="annotator",
        values="annotation",
    )
    pivot_data.reset_index(inplace=True)
    differences = pivot_data[pivot_data.annotator_1 != pivot_data.annotator_0]
    return differences


def get_final_common_df(common_df: pd.DataFrame, differences: pd.DataFrame) -> pd.DataFrame:
    unique_q_p_id = differences.q_p_id.unique()
    np.random.shuffle(unique_q_p_id)
    selected_q_p_id = unique_q_p_id[: len(unique_q_p_id) // 2]

    annotation_map = {
        (x.q_p_id, x.entity_id, x.entity): x.annotator_0
        if x.q_p_id in selected_q_p_id
        else x.annotator_1
        for x in differences.itertuples(index=False)
    }

    final_common = common_df[common_df.annotator == "annotator_0"].reset_index(drop=True)
    final_annotation = final_common[["q_p_id", "entity_id", "entity", "annotation"]].apply(
        lambda x: annotation_map.get((x.q_p_id, x.entity_id, x.entity), x.annotation), axis=1
    )
    final_common["annotation"] = final_annotation

    return final_common
