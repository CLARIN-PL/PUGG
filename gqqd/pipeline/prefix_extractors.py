from abc import ABC, abstractmethod
from typing import Sequence

import spacy
from tqdm import tqdm
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline


class PrefixExtractor(ABC):
    @abstractmethod
    def extract(self, questions: Sequence[str]) -> list[str | None]:
        pass


class SpacyPrefixExtractor(PrefixExtractor):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def extract(self, questions: Sequence[str]) -> list[str | None]:
        result = []
        nlp = spacy.load(self.model_name)
        for doc in tqdm(nlp.pipe(questions)):
            if len(doc.ents) > 0:
                ent, *_ = doc.ents
                result.append(doc.text[: ent.start_char])
            else:
                result.append(None)
        return result


class TransformerPrefixExtractor(PrefixExtractor):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def extract(self, questions: Sequence[str]) -> list[str | None]:
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForTokenClassification.from_pretrained(self.model_name)
        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        result = []
        for doc in tqdm(questions):
            ner_results = nlp(doc)
            if len(ner_results) > 0:
                result.append(doc[: ner_results[0]["start"]])
            else:
                result.append(None)
        return result


class NTokenPrefixExtractor(PrefixExtractor):
    def __init__(self, n: int) -> None:
        self.n = n

    def extract(self, questions: Sequence[str]) -> list[str | None]:
        result: list[str | None] = []
        for q in questions:
            prefix = " ".join(q.split()[: self.n])
            result.append(prefix)
        return result


class LemmatizedNTokenPrefixExtractor(PrefixExtractor):
    def __init__(self, n: int, model_name: str = "pl_core_news_lg") -> None:
        self.n = n
        self.model_name = model_name
        self.nlp = spacy.load(self.model_name, exclude=["ner", "tagger", "parser"])

    def extract(self, questions: Sequence[str]) -> list[str | None]:
        result: list[str | None] = []
        for doc in self.nlp.pipe(questions):
            tokens = [t for t in doc if not t.is_punct]
            lemmas = [t.lemma_ for t in tokens[: self.n]]
            result.append(" ".join(lemmas).lower())
        return result
