import configparser
import os
from pathlib import Path

import pandas as pd
import srsly


def load_inforex_output_df(path: Path) -> pd.DataFrame:
    annotation_path = path / "documents"
    docs = {entry.name.split(".")[0] for entry in os.scandir(annotation_path)}

    id_to_title = {}
    data = []
    for doc in sorted(docs):
        config = configparser.ConfigParser()
        config.read(annotation_path / f"{doc}.ini")
        id_to_title[config["document"]["id"]] = config["document"]["title"]

        [annotation] = srsly.read_json(annotation_path / f"{doc}.json")["annotations"]
        data.append(annotation)

    df = pd.DataFrame(data)
    cols_to_drop = [col for col in df.columns if df[col].nunique() <= 1]
    df = df.drop(columns=cols_to_drop)
    df["q_p_id"] = df.report_id.map(id_to_title)
    df = df.rename(columns={"text": "human_annotation"})
    return df
