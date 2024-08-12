import json
import random
from dataclasses import dataclass
from typing import Any, List, Optional

from gqqd.utils.utils import get_current_time_str, get_string_md5
from sqqd.api.sparql_templates.base_template import BaseTemplate
from sqqd.api.sparql_templates.mixed_template import MixedTemplate
from sqqd.api.sparql_templates.one_hop_template import OneHopTemplate
from sqqd.api.sparql_templates.one_hop_template_with_mask import OneHopTemplateWithMask
from sqqd.api.sparql_templates.reverse_one_hop_template import ReverseOneHopTemplate
from sqqd.api.sparql_templates.reverse_one_hop_template_with_mask import (
    ReverseOneHopTemplateWithMask,
)
from sqqd.api.sparql_templates.reverse_two_hop_template import ReverseTwoHopTemplate
from sqqd.api.sparql_templates.reverse_two_hop_template_with_mask import (
    ReverseTwoHopTemplateWithMask,
)
from sqqd.api.sparql_templates.two_hop_template import TwoHopTemplate
from sqqd.api.wikidata_query_client import WikidataSPARQLClient
from sqqd.defaults import PROPERTIES_PATH


@dataclass
class SPARQLQuestion:
    id: str
    base_entity: str
    template: str
    primary_question: str
    sparql_query: str
    answer_ids: List[str]
    answer_labels: List[str]
    question_entity_ids: List[str]
    question_entity_labels: List[str]
    relation_ids: List[str]
    relation_labels: List[str]
    time: str


class SPARQLQuestionClient:
    template_map = {
        "one_hop_template": OneHopTemplate,
        "one_hop_template_with_mask": OneHopTemplateWithMask,
        "two_hop_template": TwoHopTemplate,
        "reverse_one_hop_template": ReverseOneHopTemplate,
        "reverse_one_hop_template_with_mask": ReverseOneHopTemplateWithMask,
        "reverse_two_hop_template": ReverseTwoHopTemplate,
        "reverse_two_hop_template_with_mask": ReverseTwoHopTemplateWithMask,
        "mixed_template": MixedTemplate,
    }

    def __init__(
        self,
        template_name: str,
        entries_limit: int,
        random_seed: int = 42,
        wikidata_sparql_client_agent: str | None = None,
    ) -> None:
        self.template_class = self.get_template(template_name)
        self.relation_labels_dict = self.get_relation_labels_dict()
        self.wikidata_query_client = WikidataSPARQLClient(agent=wikidata_sparql_client_agent)
        self.entries_limit = entries_limit
        self.random_generator = random.Random(random_seed)

    def get_template(self, template_name: str) -> type:
        template_class = self.template_map.get(template_name)
        if template_class is None:
            raise ValueError(f"Unknown template name: {template_name}")
        return template_class

    @staticmethod
    def get_relation_labels_dict() -> dict[str, str]:
        if not PROPERTIES_PATH.exists():
            ValueError("Properties file does not exist")
        with open(PROPERTIES_PATH / "filtered_property_labels.json", "r") as f:
            relation_labels_dict: dict[str, str] = json.load(f)
        return relation_labels_dict

    def build_entry(
        self,
        chain_elements: Optional[
            tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]
        ],
        template: BaseTemplate,
        base_entity: str,
    ) -> Any:
        if not chain_elements:
            return None
        entity_ids, property_ids, entity_labels, property_labels = chain_elements
        sparql_query = template.get_sparql_query_pattern().format(**entity_ids, **property_ids)
        query_results = self.wikidata_query_client.get_query_results(sparql_query)
        if not query_results:
            return None

        results_bindings = query_results.get("results", {}).get("bindings", [])
        if len(results_bindings) > template.max_response_count or len(results_bindings) == 0:
            return None

        retrieved_ids = []
        retrieved_labels = []
        for result in results_bindings:
            answer_id = result["answerEntity"]["value"].split("/")[-1]
            if answer_id in retrieved_ids:
                continue
            answer_label = self.wikidata_query_client.get_object_name(answer_id)
            if answer_label is None:
                return None
            retrieved_ids.append(answer_id)
            retrieved_labels.append(answer_label)

        question = template.get_question_pattern().format(**entity_labels, **property_labels)
        result = SPARQLQuestion(
            id=get_string_md5(sparql_query),
            base_entity=base_entity,
            template=template.__str__(),
            primary_question=question,
            sparql_query=sparql_query,
            answer_ids=retrieved_ids,
            answer_labels=retrieved_labels,
            question_entity_ids=list(entity_ids.values()),
            question_entity_labels=list(entity_labels.values()),
            relation_ids=list(property_ids.values()),
            relation_labels=list(property_labels.values()),
            time=get_current_time_str(),
        )
        return result

    def build_questions_from_entity(self, entity_id: str) -> list[SPARQLQuestion] | None:
        entity_name = self.wikidata_query_client.get_object_name(entity_id)
        if not entity_name:
            return None

        template = self.template_class(entity_id, entity_name, self.relation_labels_dict)
        query = template.get_query_for_chains_retrieval()
        possible_chains = self.wikidata_query_client.get_query_results(query)

        if not possible_chains:
            return None
        possible_chain_bindings = possible_chains.get("results", {}).get("bindings", [])
        self.random_generator.shuffle(possible_chain_bindings)

        retrieved_data = []
        retrieved_entries_number = 0

        for chain in possible_chain_bindings:
            chain_elements = template.extract_chain_elements(chain)
            entry = self.build_entry(chain_elements, template, entity_id)
            if entry:
                retrieved_data.append(entry)
                retrieved_entries_number += 1
                if retrieved_entries_number >= self.entries_limit:
                    break

        return retrieved_data
