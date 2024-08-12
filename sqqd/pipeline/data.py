from dataclasses import dataclass
from typing import Literal

from gqqd.pipeline.output.data import KBQAExample


@dataclass(frozen=True, slots=True)
class KBQATemplateBasedExample(KBQAExample):
    sparql_query: str
    sparql_query_template: str
    type: Literal["natural", "template-based"] = "template-based"
