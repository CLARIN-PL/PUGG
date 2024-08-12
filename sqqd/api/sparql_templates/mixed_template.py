from sqqd.api.sparql_templates.base_template import BaseTemplate


class MixedTemplate(BaseTemplate):
    max_response_count = 10
    keys_to_extract = [
        "firstRelatedEntity",
        "firstRelatedEntityLabel",
        "firstRelation",
        "firstRelationLabel",
        "secondRelation",
        "secondRelationLabel",
        "substituteEntity",
        "substituteEntityLabel",
    ]

    def __init__(
        self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]
    ) -> None:
        super().__init__(entity_id, entity_name, relation_labels_dict)

    def __str__(self) -> str:
        return "Mixed Template"

    def get_query_for_chains_retrieval(self) -> str:
        chain_template = f"""
        wd:{self.entity_id} ?firstRelation ?firstRelatedEntity.
        wd:{self.entity_id} ?secondRelation ?secondRelatedEntity.
        wd:{self.entity_id} wdt:P31 ?substituteEntity.
        """
        query = f"""
        SELECT DISTINCT ?firstRelatedEntity ?firstRelatedEntityLabel ?firstRelation ?secondRelation 
            ?substituteEntity ?substituteEntityLabel
        WHERE {{
            {chain_template}
            FILTER (STRSTARTS(STR(?firstRelatedEntity), "http://www.wikidata.org/entity/Q")).
            FILTER (STRSTARTS(STR(?secondRelatedEntity), "http://www.wikidata.org/entity/Q")).
            FILTER (?firstRelatedEntity != ?secondRelatedEntity).
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl". }}
        }}
        """
        return query

    def get_sparql_query_pattern(self) -> str:
        sparql_query_template = """SELECT ?answerEntity 
WHERE {{ 
    ?bindingEntity wdt:P31 wd:{substituteEntity}.
    ?bindingEntity wdt:{firstRelation} wd:{firstRelatedEntity}.
    ?bindingEntity wdt:{secondRelation} ?answerEntity.
}}
"""
        return sparql_query_template

    def get_question_pattern(self) -> str:
        question_template = (
            "Jakie {secondRelationLabel} ma {substituteEntityLabel}, "
            "którego {firstRelationLabel} jest {firstRelatedEntityLabel}?"
        )
        return question_template
