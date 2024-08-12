from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import numpy.typing as npt
import torch
from sentence_transformers.util import cos_sim
from sklearn.preprocessing import LabelEncoder


class SubgraphRetriever(ABC):
    @abstractmethod
    def retrieve(self, topic_entities: list[str], **kwargs: Any) -> npt.NDArray[np.str_]:
        pass


class NHopRetriever(SubgraphRetriever):
    def __init__(self, n: int, triples: npt.NDArray[np.str_], **kwargs: Any):
        self.n = n
        self.triples = triples
        self.encoder = LabelEncoder()
        self.triples_encoded = self.encoder.fit_transform(triples.flatten()).reshape(triples.shape)

    def retrieve(self, topic_entities: list[str], **kwargs: Any) -> npt.NDArray[np.str_]:
        return self.build_n_hop_subgraph(topic_entities)

    def build_n_hop_subgraph(self, topic_entities: list[str]) -> npt.NDArray[np.str_]:
        topic_entities = [t for t in topic_entities if t in self.encoder.classes_]
        subgraph = self.encoder.transform(topic_entities)
        for _ in range(self.n):
            related_triples = self.triples_encoded[
                np.isin(self.triples_encoded[:, [0, 2]], subgraph).any(1)
            ]
            subgraph = np.unique(related_triples[:, [0, 2]])
        assert isinstance(subgraph, np.ndarray)
        if related_triples.size == 0:
            return np.empty((0, 3), dtype=self.triples.dtype)
        result = self.encoder.inverse_transform(related_triples.flatten()).reshape(
            related_triples.shape
        )
        assert isinstance(result, np.ndarray)
        return result


class FilteredTriplesNHopRetriever(NHopRetriever):
    def __init__(
        self,
        n: int,
        triples: npt.NDArray[np.str_],
        labels: dict[str, str],
        triples_emb: torch.Tensor,
        **kwargs: Any
    ):
        super().__init__(n, triples)
        self.labels = labels
        self.triples_emb = triples_emb
        self.triple_idx_map = {tuple(t): i for i, t in enumerate(self.triples)}

    def retrieve(self, topic_entities: list[str], **kwargs: Any) -> npt.NDArray[np.str_]:
        query_emb: torch.Tensor = kwargs["query_emb"]
        k_triples: int = kwargs["k_triples"]
        subgraph = super().retrieve(topic_entities)
        return self.retrieve_for_subgraph(subgraph, query_emb, k_triples)

    def retrieve_for_subgraph(
        self, subgraph: npt.NDArray[np.str_], query_emb: torch.Tensor, k_triples: int, **kwargs: Any
    ) -> npt.NDArray[np.str_]:
        if len(subgraph) == 0:
            return subgraph

        indices = np.array([self.triple_idx_map[tuple(t)] for t in subgraph])
        answers_emb = self.triples_emb[indices]  # type: ignore
        assert answers_emb.shape[0] == len(subgraph)

        similarities = cos_sim(query_emb, answers_emb)
        k_triples = min(k_triples, len(subgraph))
        top_triples = torch.topk(similarities, k_triples).indices[0]
        result = subgraph[top_triples].reshape(-1, 3)
        assert isinstance(result, np.ndarray)
        return result
