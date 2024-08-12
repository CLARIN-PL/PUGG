from pathlib import Path

import numpy as np
import pandas as pd
import typer
from rich import print

from gqqd.defaults import ANNOTATED_PATH, ENTITY_LINKING_INPUT

GPT_ITERATION = 0
INFOREX_ITERATION = 0


def main(
    inforex_output_iteration: int = typer.Option(...),
    output_path: Path = typer.Option(ENTITY_LINKING_INPUT),
):
    np.random.seed(17)

    output_path = output_path / str(inforex_output_iteration)
    output_path.mkdir(parents=True, exist_ok=True)

    verified_annotation_path = (
        ANNOTATED_PATH / "inforex_output_verification" / f"{inforex_output_iteration}_verified"
    )
    individual_df, common_df = load_filter_data(verified_annotation_path)
    differences = get_differences_df(common_df)
    final_common = get_final_common_df(common_df, differences)
    final_df = pd.concat([individual_df, final_common], ignore_index=True)

    verified_df = final_df[final_df.annotation == 1]
    print(f"Correct KBQA questions: {verified_df.q_p_id.nunique()}")
    print(
        f"Correct KBQA questions (%): "
        f"{verified_df.q_p_id.nunique() / final_df.q_p_id.nunique():.2%}"
    )

    output = (
        verified_df.groupby(["q_p_id", "q_id", "p_id", "question", "text"])
        .agg({"wiki_entity": list})
        .reset_index()
    )
    assert output.question.duplicated().sum() == 0

    gpt_annotated_path = ANNOTATED_PATH / f"gpt_auto_annotated_iteration_{GPT_ITERATION}.json"
    gpt_annotated_df = pd.read_json(gpt_annotated_path)
    gpt_annotated_df.rename(columns={"id": "q_id"}, inplace=True)
    gpt_annotated_df = pd.concat(
        [gpt_annotated_df, pd.json_normalize(gpt_annotated_df.passage)], axis=1
    )
    gpt_annotated_df = gpt_annotated_df.drop(columns=["passage"])
    gpt_annotated_df.set_index("q_id", inplace=True)
    output["passage_page"] = gpt_annotated_df.wiki_page.loc[output.q_id].tolist()
    output.rename(columns={"text": "passage", "wiki_entity": "answer_entities"}, inplace=True)
    assert output.passage_page.isna().sum() == 0
    output = output[
        ["q_p_id", "q_id", "p_id", "question", "passage", "passage_page", "answer_entities"]
    ]
    output.q_id = pd.Categorical(output.q_id, gpt_annotated_df.index)
    output.sort_values("q_id", inplace=True)
    output.to_json(output_path / "input.json", orient="records", indent=4, force_ascii=False)


def load_filter_data(verified_annotation_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotator_0 = pd.read_csv(verified_annotation_path / "annotator_0.csv")
    annotator_1 = pd.read_csv(verified_annotation_path / "annotator_1.csv")

    for annotator_df in [annotator_0, annotator_1]:
        for col in ["q_p_id", "q_id", "p_id", "question", "text"]:
            annotator_df[col].fillna(method="ffill", inplace=True)

    annotator_0.drop_duplicates(subset=["q_p_id", "question", "wiki_entity"], inplace=True)
    annotator_1.drop_duplicates(subset=["q_p_id", "question", "wiki_entity"], inplace=True)

    df = (
        pd.concat(
            [annotator_0, annotator_1],
            keys=["annotator_0", "annotator_1"],
            names=["annotator", "index"],
        )
        .reset_index()
        .drop(columns="index")
    )
    to_remove = df[~(df.note.isna() | df.note.str.isspace())].q_p_id.unique()
    df = df[~df.q_p_id.isin(to_remove)].reset_index(drop=True)

    common_q_p_id = set(annotator_0.q_p_id.unique()) & set(annotator_1.q_p_id.unique())
    individual_q_p_id = (
        set(annotator_0.q_p_id.unique()) | set(annotator_1.q_p_id.unique())
    ) - common_q_p_id

    individual_df = df[df.q_p_id.isin(individual_q_p_id)].reset_index(drop=True)
    common_df = df[df.q_p_id.isin(common_q_p_id)].reset_index(drop=True)

    assert individual_df.annotation.isna().sum() == 0
    assert common_df.annotation.isna().sum() == 0

    print(f"Number of individual questions: {individual_df.q_p_id.nunique()}")
    print(f"Number of common questions: {common_df.q_p_id.nunique()}")
    return individual_df, common_df


def get_differences_df(common_df: pd.DataFrame) -> pd.DataFrame:
    pivot_data = common_df.pivot(
        index=["q_p_id", "question", "wiki_entity"], columns="annotator", values="annotation"
    )
    pivot_data.reset_index(inplace=True)
    pivot_data = pivot_data[pivot_data.annotator_1.notna() & pivot_data.annotator_0.notna()]
    differences = pivot_data[pivot_data.annotator_1 != pivot_data.annotator_0]
    return differences


def get_final_common_df(common_df: pd.DataFrame, differences: pd.DataFrame) -> pd.DataFrame:
    unique_q_p_id = differences.q_p_id.unique()
    np.random.shuffle(unique_q_p_id)
    selected_q_p_id = unique_q_p_id[: len(unique_q_p_id) // 2]

    annotation_map = {
        (x.q_p_id, x.wiki_entity): x.annotator_0 if x.q_p_id in selected_q_p_id else x.annotator_1
        for x in differences.itertuples(index=False)
    }

    final_common = common_df[common_df.annotator == "annotator_0"].reset_index(drop=True)
    final_annotation = final_common[["q_p_id", "wiki_entity", "annotation"]].apply(
        lambda x: annotation_map.get((x.q_p_id, x.wiki_entity), x.annotation), axis=1
    )
    final_common["annotation"] = final_annotation
    return final_common


typer.run(main)
