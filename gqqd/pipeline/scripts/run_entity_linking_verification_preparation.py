import random
from pathlib import Path

import numpy as np
import pandas as pd
import typer
from tinydb import TinyDB

from gqqd.defaults import ENTITY_LINKING_ANNOTATION, ENTITY_LINKING_OUTPUT
from gqqd.utils.excell_utils import format_links, merge_cells_for_columns, wrap_text
from gqqd.utils.utils import split_list_with_weights

WIKI_LINK_PREFIX = "https://pl.wikipedia.org/wiki/"

SHEET_NAME = "annotation"
OUTPUT_PATH = ENTITY_LINKING_ANNOTATION / "input"


np.random.seed(17)
random.seed(17)


def main(
    iteration: int = typer.Option(...),
    annotator: list[float] = typer.Option(...),
    common_examples_factor: float = typer.Option(0.10),
    output_path: Path = typer.Option(OUTPUT_PATH),
) -> None:
    assert sum(annotator) == 1.0
    num_annotators = len(annotator)
    output_path = output_path / str(iteration)
    output_path.mkdir(parents=True, exist_ok=True)
    df = load_data(iteration)
    df["entity"] = df["entity"].apply(lambda x: WIKI_LINK_PREFIX + x)
    df["annotation"] = ""
    df["note"] = ""
    df = df[
        [
            "q_p_id",
            "q_id",
            "p_id",
            "entity_id",
            "question",
            "entity",
            "annotation",
            "note",
            "answer_entities",
        ]
    ]

    df = df.reset_index(drop=True)
    ids = df.q_p_id.unique()
    np.random.shuffle(ids)

    common_examples = ids[: int(common_examples_factor * len(ids))]
    annotators = split_list_with_weights(
        ids[len(common_examples) :], annotator, num_groups=num_annotators
    )

    assert len(common_examples) + sum(len(x) for x in annotators) == len(ids)
    print(f"Common examples: {len(common_examples)}")
    print(f"Annotators examples: {[len(x) for x in annotators]}")

    for i in range(num_annotators):
        df_annotator = df[df.q_p_id.isin(common_examples) | df.q_p_id.isin(annotators[i])]
        print(f"Annotator {i}: {len(df_annotator.q_p_id.unique())} final examples.")

        with pd.ExcelWriter(output_path / f"annotator_{i}.xlsx", engine="openpyxl") as excel_writer:
            df_annotator.to_excel(excel_writer, index=False, sheet_name=SHEET_NAME)

            format_links(
                excel_writer, SHEET_NAME, col_idx=df_annotator.columns.get_loc("entity") + 1
            )
            merge_cells_for_columns(excel_writer, SHEET_NAME, df_annotator)

            wrap_text(
                excel_writer,
                SHEET_NAME,
                col_idx=df_annotator.columns.get_loc("question") + 1,
                len_df=len(df_annotator),
                height=30,
            )
            wrap_text(
                excel_writer,
                SHEET_NAME,
                col_idx=df_annotator.columns.get_loc("answer_entities") + 1,
                len_df=len(df_annotator),
                height=30,
            )


def load_data(iteration: int) -> pd.DataFrame:
    entity_linking_output = ENTITY_LINKING_OUTPUT / f"{iteration}/output.json"
    df = pd.DataFrame(TinyDB(entity_linking_output).table("results").all())

    def create_pairs(row):
        assert len(row.values) == 2
        return [(a, b) for a, b in zip(row.values[0], row.values[1], strict=True)]

    df["entity"] = (
        df[["question_direct_entities", "question_direct_entities_ids"]].apply(create_pairs, axis=1)
        + df[["question_associated_entities", "question_associated_entities_ids"]].apply(
            create_pairs, axis=1
        )
        + df[["passage_page", "passage_page_id"]].apply(lambda x: [tuple(x)], axis=1)
    )

    def remove_duplicates_from_list(l: list) -> list:
        seen = set()
        return [x for x in l if not (x in seen or seen.add(x))]

    df.entity = df.entity.apply(remove_duplicates_from_list)
    df = df.explode("entity").reset_index(drop=True)
    df = df.dropna(subset=["entity"])

    df = df.drop(
        columns=[
            "question_direct_entities",
            "question_direct_entities_ids",
            "question_associated_entities",
            "question_associated_entities_ids",
            "passage",
            "passage_page",
            "passage_page_id",
            "answer_entities_ids",
        ]
    )
    df["entity_id"] = df.entity.apply(lambda x: x[1])
    df["entity"] = df.entity.apply(lambda x: x[0])
    return df


typer.run(main)
