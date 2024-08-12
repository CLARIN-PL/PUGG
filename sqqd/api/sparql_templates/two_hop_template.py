from sqqd.api.sparql_templates.base_template import BaseTemplate


class TwoHopTemplate(BaseTemplate):
    keys_to_extract = [
        "mainEntity",
        "mainEntityLabel",
        "firstRelation",
        "firstRelationLabel",
        "secondRelation",
        "secondRelationLabel",
    ]
    max_response_count = 10

    def __init__(
        self, entity_id: str, entity_name: str, relation_labels_dict: dict[str, str]
    ) -> None:
        super().__init__(entity_id, entity_name, relation_labels_dict)

    def __str__(self) -> str:
        return "Two Hop Template"

    def get_query_for_chains_retrieval(self) -> str:
        chain_template = f"""
        wd:{self.entity_id} ?firstRelation ?firstRelatedEntity. 
        ?firstRelatedEntity ?secondRelation ?secondRelatedEntity.
        """
        query = f"""
        SELECT DISTINCT ?firstRelation ?secondRelation
        WHERE {{ 
            {chain_template} 
            FILTER (?firstRelation != ?secondRelation)
            FILTER (STRSTARTS(STR(?firstRelatedEntity), "http://www.wikidata.org/entity/Q"))
            FILTER (STRSTARTS(STR(?secondRelatedEntity), "http://www.wikidata.org/entity/Q"))
        }}
        """
        return query

    def get_sparql_query_pattern(self) -> str:
        sparql_query_template = """SELECT ?answerEntity 
WHERE {{ 
    wd:{mainEntity} wdt:{firstRelation} ?firstRelatedEntity .
    ?firstRelatedEntity wdt:{secondRelation} ?answerEntity 
}}
"""
        return sparql_query_template

    def get_question_pattern(self) -> str:
        question_template = "Jakie {secondRelationLabel} ma {firstRelationLabel} {mainEntityLabel}?"
        return question_template
