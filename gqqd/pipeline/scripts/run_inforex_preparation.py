import re
from pathlib import Path
from typing import Iterator

import pandas as pd
import srsly
import typer

from gqqd.data.inforex import load_inforex_output_df
from gqqd.defaults import ANNOTATED_PATH
from gqqd.utils.utils import get_string_md5


def main(
    input_path: Path = typer.Option(None),
    output_path: Path = typer.Option(None),
    iteration: int = typer.Option(0),
) -> None:
    if input_path is None:
        input_path = ANNOTATED_PATH / f"gpt_auto_annotated_iteration_{iteration}.json"

    data = list(srsly.read_json(input_path))
    df = pd.DataFrame(data)
    df = pd.concat([df, pd.json_normalize(df.passage)], axis=1)
    df = df.rename(columns={"id": "q_id"})
    df["q_p_id"] = (df.question + df.text).apply(get_string_md5)
    df["p_id"] = df.text.apply(get_string_md5)

    already_done = get_already_done()
    df = df[~df.q_p_id.isin(already_done)]

    out = df[["q_p_id", "q_id", "p_id", "question", "text", "gpt_answer", "span"]]

    assert all(
        entry.text[entry.span[0] : entry.span[1]] == entry.gpt_answer for entry in out.itertuples()
    )

    out.insert(len(out.columns), "inforex_span", list(inforex_spans(out)))

    for entry in out.itertuples():
        assert (
            entry.gpt_answer.replace(" ", "")
            == entry.text.replace(" ", "")[entry.inforex_span[0] : entry.inforex_span[1]]
        )

    if output_path is None:
        output_path = ANNOTATED_PATH / f"inforex_input_iteration_{iteration}.json"

    out.to_json(output_path, orient="records", indent=4, force_ascii=False)


def inforex_spans(df: pd.DataFrame) -> Iterator[list[int]]:
    for entry in df.itertuples():
        assert entry.text.count(" ") == len(re.findall(r"(\s)", entry.text))
        inforex_span = []
        for idx in entry.span:
            assert entry.text[:idx].count(" ") == len(re.findall(r"(\s)", entry.text[:idx]))
            inforex_span.append(idx - entry.text[:idx].count(" "))
        yield inforex_span


def get_already_done() -> set[str]:
    already_done = set()
    for export_name in ["inforex_export_756", "inforex_export_758", "inforex_export_759"]:
        df = load_inforex_output_df(ANNOTATED_PATH / f"inforex/{export_name}")
        already_done.update(df["q_p_id"].unique())
    return already_done


typer.run(main)
