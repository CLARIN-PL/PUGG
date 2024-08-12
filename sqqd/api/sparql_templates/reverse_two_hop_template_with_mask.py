from sqqd.api.sparql_templates.base_template import BaseTemplate


class ReverseTwoHopTemplateWithMask(BaseTemplate):
    max_response_count = 10
    keys_to_extract = [
        "firstRelatedEntity",
        "firstRelatedEntityLabel",
        "firstRelation",
        "firstRelationLabel",
        "secondRelatedEntity",
        "secondRelatedEntityLabel",
        "secondRelation",
        "secondRelationLabel",
        "substituteEntity",
        "substituteEntityLabel",
    ]

    def __init__(self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]):
        super().__init__(entity_id, entity_name, relation_labels_dict)

    def __str__(self) -> str:
        return "Reverse Two Hop Template With Mask"

    def get_query_for_chains_retrieval(self) -> str:
        chain_template = f"""
        wd:{self.entity_id} ?firstRelation ?firstRelatedEntity.
        wd:{self.entity_id} ?secondRelation ?secondRelatedEntity.
        wd:{self.entity_id} wdt:P31 ?substituteEntity.
        """

        query = f"""SELECT ?firstRelatedEntity ?firstRelatedEntityLabel ?firstRelation ?secondRelatedEntity 
            ?secondRelatedEntityLabel ?secondRelation ?substituteEntity ?substituteEntityLabel
        WHERE {{ 
            {chain_template}
            FILTER (STRSTARTS(STR(?firstRelatedEntity), "http://www.wikidata.org/entity/Q")) 
            FILTER (STRSTARTS(STR(?secondRelatedEntity), "http://www.wikidata.org/entity/Q")) .
            FILTER (?firstRelatedEntity != ?secondRelatedEntity)
            FILTER (?firstRelation != ?secondRelation)
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl". }}
        }}
        """
        return query

    def get_sparql_query_pattern(self) -> str:
        sparql_query_template = """SELECT ?answerEntity 
WHERE {{ 
    ?answerEntity wdt:{firstRelation} wd:{firstRelatedEntity}.
    ?answerEntity wdt:{secondRelation} wd:{secondRelatedEntity}.
    ?answerEntity wdt:P31 wd:{substituteEntity}.
}}
"""
        return sparql_query_template

    def get_question_pattern(self) -> str:
        question_template = (
            "Jak nazywał się {substituteEntityLabel}, "
            "którego {firstRelationLabel} jest {firstRelatedEntityLabel}, "
            "a którego {secondRelationLabel} jest {secondRelatedEntityLabel}?"
        )
        return question_template
