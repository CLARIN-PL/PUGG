from abc import ABC, abstractmethod
from typing import Optional


class BaseTemplate(ABC):
    max_response_count: int
    keys_to_extract: list[str]

    def __init__(
        self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]
    ) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.relation_labels_dict = relation_labels_dict

    def __init_subclass__(cls) -> None:
        for required in (
            "max_response_count",
            "keys_to_extract",
        ):
            if not getattr(cls, required):
                raise TypeError(
                    f"Can't instantiate abstract class {cls.__name__} without {required} attribute defined"
                )
        return super().__init_subclass__()

    @abstractmethod
    def get_query_for_chains_retrieval(self) -> str:
        pass

    @abstractmethod
    def get_sparql_query_pattern(self) -> str:
        pass

    @abstractmethod
    def get_question_pattern(self) -> str:
        pass

    def extract_chain_elements(
        self, item: dict[str, dict[str, str]]
    ) -> Optional[tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]]:
        relation_label_keys = [
            key for key in self.keys_to_extract if key.endswith(("RelationLabel", "relationLabel"))
        ]
        entity_label_keys = [
            key for key in self.keys_to_extract if key.endswith(("EntityLabel", "entityLabel"))
        ]
        relation_id_keys = [
            key for key in self.keys_to_extract if key.endswith(("Relation", "relation"))
        ]
        entity_id_keys = [key for key in self.keys_to_extract if key.endswith(("Entity", "entity"))]

        extracted_entity_ids = {}
        extracted_relation_ids = {}
        extracted_entity_labels = {}
        extracted_relation_labels = {}

        for key in entity_id_keys:
            if key.startswith("main"):
                extracted_entity_ids[key] = self.entity_id
            elif key in item:
                extracted_entity_ids[key] = item[key]["value"].split("/")[-1]
            else:
                raise ValueError(f"Key {key} not found in retrieved chain {item}.")

        for key in relation_id_keys:
            if key in item:
                extracted_relation_ids[key] = item[key]["value"].split("/")[-1]
            else:
                raise ValueError(f"Key {key} not found in retrieved chain {item}.")

        for key in entity_label_keys:
            if key.startswith("main"):
                extracted_entity_labels[key] = self.entity_name
            elif key in item:
                if item[key]["value"].startswith("Q"):
                    return None
                extracted_entity_labels[key] = item[key]["value"]
            else:
                raise ValueError(f"Key {key} not found in retrieved chain {item}.")

        for key in relation_label_keys:
            if key[:-5] not in extracted_relation_ids:
                raise ValueError(f"Key {key} cannot be extracted without its relation id.")
            if extracted_relation_ids[key[:-5]] not in self.relation_labels_dict:
                return None
            extracted_relation_labels[key] = self.relation_labels_dict[
                extracted_relation_ids[key[:-5]]
            ]

        return (
            extracted_entity_ids,
            extracted_relation_ids,
            extracted_entity_labels,
            extracted_relation_labels,
        )
