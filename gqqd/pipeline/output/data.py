from abc import ABC
from dataclasses import dataclass, field
from typing import Literal

from gqqd.utils.utils import get_string_md5


@dataclass(frozen=True, slots=True)
class TextualAnswer:
    text: str
    answer_start: int
    answer_end: int


@dataclass(frozen=True, slots=True)
class WikiLink:
    start_idx: int
    end_idx: int
    wiki_link: str


@dataclass(frozen=True, slots=True)
class Passage:
    text: str
    links: list[WikiLink]
    wiki_page: str
    time_acquired: str


@dataclass(frozen=True, slots=True)
class Example:
    id: str = field(init=False)
    question: str
    answer: list[TextualAnswer] | None
    passages: list[Passage]
    prefix: str
    prefix_from: list[str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", get_string_md5(self.question))


@dataclass(frozen=True, slots=True)
class KBQAEntity:
    entity_id: str
    entity_label: str


@dataclass(frozen=True, slots=True)
class KBQAExample(ABC):
    id: str
    question: str
    topic: list[KBQAEntity]
    answer: list[KBQAEntity]


@dataclass(frozen=True, slots=True)
class KBQANaturalExample(KBQAExample):
    type: Literal["natural", "Template-based"] = "natural"
