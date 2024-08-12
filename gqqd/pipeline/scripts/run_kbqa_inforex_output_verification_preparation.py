import itertools
import random
from pathlib import Path

import numpy as np
import pandas as pd
import typer

from gqqd.data.inforex import load_inforex_output_df
from gqqd.data.loaders import load_wiki_content_df
from gqqd.defaults import ANNOTATED_PATH, INFOREX_OUTPUT_VERIFICATION
from gqqd.utils.excell_utils import color_spans, format_links, merge_cells_for_columns, wrap_text
from gqqd.utils.utils import split_list_with_weights

SHEET_NAME = "annotation"
OUTPUT_PATH = INFOREX_OUTPUT_VERIFICATION

INPUT_ITERATION = 0
INFOREX_OUTPUT_ID_MAP = {0: 809, 1: 904}

np.random.seed(17)
random.seed(17)


def main(
    inforex_iteration: int = typer.Option(...),
    annotator: list[float] = typer.Option([]),
    common_examples_factor: float = typer.Option(0.10),
    output_path: Path = typer.Option(OUTPUT_PATH),
) -> None:
    assert sum(annotator) == 1.0
    num_annotators = len(annotator)
    output_path = output_path / str(inforex_iteration)
    output_path.mkdir(parents=True, exist_ok=True)
    df = load_data(inforex_iteration)
    df = df.explode("links")
    df = df[df["links"].notna()]
    df["wiki_entity"] = df["links"].apply(lambda x: x["wiki_link"])
    df["annotation"] = ""
    df["note"] = ""

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
        spans = df_annotator["span"]
        df_annotator = df_annotator[
            ["q_p_id", "q_id", "p_id", "question", "text", "wiki_entity", "annotation", "note"]
        ]
        print(f"Annotator {i}: {len(df_annotator.q_p_id.unique())} final examples.")

        with pd.ExcelWriter(output_path / f"annotator_{i}.xlsx", engine="openpyxl") as excel_writer:
            df_annotator.to_excel(excel_writer, index=False, sheet_name=SHEET_NAME)

            color_spans(
                excel_writer,
                SHEET_NAME,
                col_idx=df_annotator.columns.get_loc("text") + 1,
                spans=spans,
            )
            format_links(
                excel_writer, SHEET_NAME, col_idx=df_annotator.columns.get_loc("wiki_entity") + 1
            )
            merge_cells_for_columns(excel_writer, SHEET_NAME, df_annotator)

            wrap_text(
                excel_writer,
                SHEET_NAME,
                col_idx=df_annotator.columns.get_loc("question") + 1,
                len_df=len(df_annotator),
            )
            wrap_text(
                excel_writer,
                SHEET_NAME,
                col_idx=df_annotator.columns.get_loc("text") + 1,
                len_df=len(df_annotator),
            )


def load_data(inforex_iteration: int) -> pd.DataFrame:
    gpt_annotated_path = Path(
        ANNOTATED_PATH / f"gpt_auto_annotated_iteration_{INPUT_ITERATION}.json"
    )
    inforex_input_path = Path(ANNOTATED_PATH / f"inforex_input_iteration_{INPUT_ITERATION}.json")
    inforex_output_id = INFOREX_OUTPUT_ID_MAP[inforex_iteration]
    inforex_output_path = Path(ANNOTATED_PATH / f"inforex/inforex_export_{inforex_output_id}")

    inforex_input_df = pd.read_json(inforex_input_path)
    inforex_output_df = load_inforex_output_df(inforex_output_path)

    assert inforex_iteration in {0, 1}
    if inforex_iteration == 1:
        previous_q_p_id = load_inforex_output_df(
            Path(ANNOTATED_PATH / f"inforex/inforex_export_{INFOREX_OUTPUT_ID_MAP[0]}")
        ).q_p_id
        masked_df = inforex_output_df[~inforex_output_df.q_p_id.isin(previous_q_p_id)]
        print(
            f"Filtered out {len(inforex_output_df) - len(masked_df)} "
            f"examples from previous iteration."
        )
        inforex_output_df = masked_df.reset_index(drop=True)

    gpt_annotated_df = pd.read_json(gpt_annotated_path)
    gpt_annotated_df.rename(columns={"id": "q_id"}, inplace=True)

    correct_q_p_id_set = set(inforex_output_df.q_p_id)
    correct_q_id_set = set(inforex_input_df[inforex_input_df.q_p_id.isin(correct_q_p_id_set)].q_id)
    correct_gpt_annotation = gpt_annotated_df[gpt_annotated_df.q_id.isin(correct_q_id_set)]

    correct_gpt_annotation["q_p_id"] = correct_gpt_annotation.q_id.map(
        dict(zip(inforex_input_df.q_id, inforex_input_df.q_p_id))
    )
    correct_gpt_annotation["p_id"] = correct_gpt_annotation.q_p_id.map(
        dict(zip(inforex_input_df.q_p_id, inforex_input_df.p_id))
    )

    df = correct_gpt_annotation.reset_index(drop=True)
    df = pd.concat([df, pd.json_normalize(df.passage)], axis=1)
    df = df.drop(columns=["passage"])

    content_df = load_wiki_content_df()
    content_map = dict(zip(content_df.page, content_df.plain_text))

    [prefix] = set(
        itertools.chain.from_iterable(
            df.links.apply(
                lambda x: set("/".join(link["wiki_link"].split("/")[:4]) + "/" for link in x)
            )
        )
    )
    beginning_of_page = df.apply(lambda x: content_map[x.wiki_page].startswith(x.text), axis=1)
    df.loc[beginning_of_page, "links"] = (
        df[beginning_of_page].apply(
            lambda x: [
                {
                    "start_idx": 0,
                    "end_idx": len(x.text.split(" – ")[0]),
                    "wiki_link": f"{prefix}{x.wiki_page}",
                }
            ],
            axis=1,
        )
        + df[beginning_of_page].links
    )

    df["links"] = df.apply(lambda x: filter_links_by_span(x.links, x.span), axis=1)
    return df


def filter_links_by_span(
    links: list[dict[str, int | str]], span: tuple[int, int]
) -> list[dict[str, int | str]]:
    start_idx, end_idx = span
    filtered_links = []
    for link in links:
        link_start = link["start_idx"]
        link_end = link["end_idx"]
        assert isinstance(link_start, int)
        assert isinstance(link_end, int)
        if link_start <= end_idx and link_end >= start_idx:
            filtered_links.append(link)
    return filtered_links


typer.run(main)
