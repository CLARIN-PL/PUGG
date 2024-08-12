from abc import ABC, abstractmethod
from typing import Sequence

import pandas as pd

from gqqd.data.loaders import get_correct_prefixes, get_search_results_df
from gqqd.pipeline.prefix_extractors import LemmatizedNTokenPrefixExtractor


class QuestionFilter(ABC):
    @abstractmethod
    def is_ok(self, question: str) -> bool:
        pass

    def filter(self, questions: Sequence[str]) -> Sequence[str]:
        result = []
        for q in questions:
            if self.is_ok(q):
                result.append(q)
        return result


class SequentialFilter(QuestionFilter):
    def __init__(self, filters: Sequence[QuestionFilter]):
        self.filters = filters

    def filter(self, questions: Sequence[str]) -> Sequence[str]:
        for filter_ in self.filters:
            questions = filter_.filter(questions)
        return questions

    def is_ok(self, question: str) -> bool:
        return all(filter_.is_ok(question) for filter_ in self.filters)


class WikipediaInSearchExistenceFilter(QuestionFilter):
    def __init__(self, search_results: pd.DataFrame | None = None):
        if search_results is None:
            search_results = get_search_results_df()
        self.search_results = search_results

    def is_ok(self, question: str) -> bool:
        search_mask = self.search_results["query"] == question
        if search_mask.sum() < 1:
            raise ValueError(f"Question {question} not found in search results.")
        [row] = self.search_results[search_mask].iloc
        return not row.isna()["results.min_wikipedia_position"]


class PrefixCorrectFilter(QuestionFilter):
    def __init__(self) -> None:
        self.correct_prefixes = get_correct_prefixes()
        self.extractor = LemmatizedNTokenPrefixExtractor(4)

    def is_ok(self, question: str) -> bool:
        [prefix] = self.extractor.extract([question])
        assert prefix is not None
        return any(prefix.startswith(correct_prefix) for correct_prefix in self.correct_prefixes)
