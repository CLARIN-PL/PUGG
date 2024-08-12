import spacy

from gqqd.api.utils.association_lookup_utils import create_extended_word_set
from gqqd.api.utils.entity_linking_utils import (
    capitalize_every_word,
    get_top_n_wiki_search_result,
    search_mentioned,
    two_texts_similarity,
)

SPACY_MODEL = "pl_core_news_lg"


class EntityLinkingClient:
    def __init__(self) -> None:
        self.nlp = spacy.load(SPACY_MODEL)

    def extract_exact_entities(self, text: str) -> set[str]:
        """
        Extracts one-word entities which are directly presented in the question.

        Args:
           text (str): the text to extract entities from

        Returns:
           set[str]: the set of exact entities found in the text
        """
        doc = self.nlp(text)
        entities = []
        for token in doc:
            if token.pos_ in ["NOUN", "ADJ", "PROPN", "X"]:
                results = get_top_n_wiki_search_result(token.lemma_)
                for result in results:
                    if result is not None and two_texts_similarity(token.lemma_, result) > 1.5:
                        entities.append(result)
        return set(entities)

    def extract_mentioned_named_entities(self, text: str, neighbours: list[str]) -> set[str]:
        """
        Extracts named entities that are mentioned in the text and are in the neighborhood.

        Args:
            text (str): the text to extract entities from
            neighbours (list[str]): a list of entities that are related to the text.

        Returns:
            set[str]: the set of mentioned named entities found in the text
        """
        text = capitalize_every_word(text)
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            enc = search_mentioned(ent.text, neighbours)
            if enc is not None:
                entities.append(enc)
            enc = search_mentioned(ent.lemma_, neighbours)
            if enc is not None:
                entities.append(enc)
        return set(entities)

    def extract_mentioned_entities(self, text: str, neighbours: list[str]) -> set[str]:
        """
        Extracts one-or-more-word entities, even when they are replaced by synonyms or even when they consist more than of one word.

        Args:
            text (str): the text to extract entities from
            neighbours (list[str]): a list of entities that could be mentioned in the text.

        Returns:
            set[str]: the set of mentioned entities found in the text
        """
        doc = self.nlp(text)
        entities = []
        for token in doc:
            if token.pos_ == "NOUN":
                noun_tokens = [child for child in token.children if child.pos_ in ["NOUN", "PROPN"]]
                noun_query = " ".join([token.text] + [noun.text for noun in noun_tokens])
                noun_query_lemma = " ".join([token.lemma_] + [noun.lemma_ for noun in noun_tokens])

                adj_tokens = [child for child in token.children if child.pos_ == "ADJ"]
                adj_query = " ".join([token.text] + [adj.text for adj in adj_tokens])
                adj_query_lemma = " ".join([token.lemma_] + [adj.lemma_ for adj in adj_tokens])

                for query in [
                    token.text,
                    token.lemma_,
                    noun_query,
                    noun_query_lemma,
                    adj_query,
                    adj_query_lemma,
                ]:
                    extended_ent = search_mentioned(query, neighbours)
                    if extended_ent is not None and extended_ent not in entities:
                        entities.append(extended_ent)

        for token in doc:
            if token.pos_ in ["ADJ", "PROPN", "X"]:
                ent = search_mentioned(token.lemma_, neighbours)
                if ent is not None and ent not in entities:
                    entities.append(ent)
        return set(entities)

    def get_associated_pages(self, question: str, wiki_pages: list[str]) -> list[str]:
        """
        Given a question and a list of Wikipedia pages retrieved from the search engine, returns pages which does not
        contain the answer to that question in the title.

        These pages were provided by the search engine, which means that they are somehow associated with the
        question and can be used in the future as additional entities.

        Args:
            question (str): The text of the question to be answered.
            wiki_pages (list[str]): A list of candidate Wikipedia page titles.

        Returns:
            list[str]: A list of Wikipedia page titles that are associated with the question.
        """
        question_word_set = create_extended_word_set(question, self.nlp)
        appropriate_pages = []
        for wiki_page in wiki_pages:
            wiki_page_word_set = create_extended_word_set(wiki_page, self.nlp)
            if len(question_word_set & wiki_page_word_set) > 0:
                appropriate_pages.append(wiki_page)
        return appropriate_pages

    def get_results(
        self, question: str, neighbours: list[str], wiki_pages: list[str]
    ) -> tuple[set[str], list[str]]:
        exact_entities = self.extract_exact_entities(question)
        named_entities = self.extract_mentioned_named_entities(question, neighbours)
        other_entities = self.extract_mentioned_entities(question, neighbours)
        direct_entities = exact_entities.union(named_entities, other_entities)
        associated_ents = self.get_associated_pages(question, wiki_pages)
        return direct_entities, associated_ents
