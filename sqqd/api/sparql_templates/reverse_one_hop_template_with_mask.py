from sqqd.api.sparql_templates.base_template import BaseTemplate


class ReverseOneHopTemplateWithMask(BaseTemplate):
    max_response_count = 10
    keys_to_extract = [
        "relatedEntity",
        "relatedEntityLabel",
        "relation",
        "relationLabel",
        "substituteEntity",
        "substituteEntityLabel",
    ]

    def __init__(
        self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]
    ) -> None:
        super().__init__(entity_id, entity_name, relation_labels_dict)

    def __str__(self) -> str:
        return "Reverse One Hop Template With Mask"

    def get_query_for_chains_retrieval(self) -> str:
        chain_template = f"""
        wd:{self.entity_id} ?relation ?relatedEntity.
        wd:{self.entity_id} wdt:P31 ?substituteEntity.
        """
        query = f"""
        SELECT ?relatedEntity ?relatedEntityLabel ?relation ?substituteEntity ?substituteEntityLabel  
        WHERE {{ 
            {chain_template} 
            FILTER (STRSTARTS(STR(?relatedEntity), "http://www.wikidata.org/entity/Q")) 
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl". }}
        }}
        """
        return query

    def get_sparql_query_pattern(self) -> str:
        sparql_query_template = """SELECT ?answerEntity 
WHERE {{ 
    ?answerEntity wdt:{relation} wd:{relatedEntity}.
    ?answerEntity wdt:P31 wd:{substituteEntity}.
}}
"""
        return sparql_query_template

    def get_question_pattern(self) -> str:
        question_template = (
            "Jak nazywał się {substituteEntityLabel}, "
            "którego {relationLabel} jest {relatedEntityLabel}?"
        )
        return question_template
