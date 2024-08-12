from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import pandas as pd
import srsly

from gqqd.defaults import CZYWIESZ_DATASET_PATH, POQUAD_DATASET_PATH

LoaderOutput = TypeVar("LoaderOutput")


class Loader(ABC, Generic[LoaderOutput]):
    @abstractmethod
    def load(self) -> LoaderOutput:
        pass


class CzyWieszLoader(Loader[pd.DataFrame]):
    def load(self) -> pd.DataFrame:
        data = pd.read_csv(CZYWIESZ_DATASET_PATH / "czywiesz.csv", sep=";", header=None)
        data = data.rename(columns={0: "id", 1: "question"})
        return data


class PoquadLoader(Loader[pd.DataFrame]):
    def load(self) -> pd.DataFrame:
        data = srsly.read_json(POQUAD_DATASET_PATH / "question-answering_PoQuAD_poquad_train.json")[
            "data"
        ]
        for row in data:
            [row["paragraphs"]] = row["paragraphs"]
        df = pd.json_normalize(data)
        df = df.explode("paragraphs.qas").reset_index(drop=True)
        df = pd.concat([df, pd.json_normalize(df["paragraphs.qas"])], axis=1).drop(
            "paragraphs.qas", axis=1
        )
        df = df.dropna(subset=["question"])
        return df
