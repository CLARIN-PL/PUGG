import difflib
from typing import Optional

import requests

WIKI_API_ENDPOINT = (
    "https://pl.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch="
)


def capitalize_every_word(text: str) -> str:
    # we need capitalization to allow spacy extract named entities
    # (without capitalization it doesn't see entities at all, so it's better to capitalize every word)
    # (after capitalization named entities are extracted almost always)
    return " ".join([word.capitalize() for word in text.split(" ")])


def get_top_n_wiki_search_result(search_query: str, n: int = 3) -> list[str]:
    assert n > 0
    result = requests.get(WIKI_API_ENDPOINT + search_query).json()
    search_results = result["query"]["search"]
    top_results = [result for result in search_results[:n]]
    return [result["title"] for result in top_results]


def two_texts_similarity(word1: str, word2: str) -> float:
    # measures the similarity by the longest common sequence and by the longest common prefix
    word1 = word1.lower()
    word2 = word2.lower()

    matcher = difflib.SequenceMatcher(None, word1, word2)
    match = matcher.find_longest_match(0, len(word1), 0, len(word2))

    beginning_score = 0
    for i in range(min(len(word1), (len(word2)))):
        if word1[i] == word2[i]:
            beginning_score += 1
    return (match.size + beginning_score) / len(word2)


def search_mentioned(query: str, target_titles: list[str], top_n: int = 3) -> Optional[str]:
    query.lower()
    decapitalized_titles = [title.lower() for title in target_titles]
    top_three_results = get_top_n_wiki_search_result(query, top_n)
    for result in top_three_results:
        if result.lower() in decapitalized_titles:
            return result
    return None
