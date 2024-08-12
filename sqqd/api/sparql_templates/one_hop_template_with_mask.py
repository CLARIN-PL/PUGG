from sqqd.api.sparql_templates.base_template import BaseTemplate


class OneHopTemplateWithMask(BaseTemplate):
    keys_to_extract = [
        "mainEntity",
        "mainEntityLabel",
        "relation",
        "relationLabel",
        "substituteEntity",
        "substituteEntityLabel",
    ]
    max_response_count = 10

    def __init__(self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]):
        super().__init__(entity_id, entity_name, relation_labels_dict)

    def __str__(self) -> str:
        return "One Hop Template With Mask"

    def get_query_for_chains_retrieval(self) -> str:
        chain_template = f"""
        wd:{self.entity_id} ?relation ?relatedEntity.
        ?relatedEntity wdt:P31 ?substituteEntity. 
        """
        query = f"""
        SELECT DISTINCT ?relation ?substituteEntity ?substituteEntityLabel 
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
    wd:{mainEntity} wdt:{relation} ?answerEntity.
    ?answerEntity wdt:P31 wd:{substituteEntity}. 
}}
"""
        return sparql_query_template

    def get_question_pattern(self) -> str:
        question_template = (
            "Jak nazywał się {substituteEntityLabel}, "
            "który jest {relationLabel} {mainEntityLabel}?"
        )
        return question_template
