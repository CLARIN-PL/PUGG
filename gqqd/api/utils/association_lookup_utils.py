from spacy.language import Language


def _lemmatize_tokens(text: str, nlp: Language) -> set[str]:
    doc = nlp(text)
    word_set = set()
    for token in doc:
        if token.pos_ not in ["AUX", "PRON", "ADP"]:
            word_set.add(token.lemma_)
    return word_set


def _lemmatize_repeatedly(word_set: set[str], nlp: Language) -> set[str]:
    new_word_set = set()
    for word in word_set:
        doc = nlp(word)
        for token in doc:
            new_word_set.add(token.lemma_)
    return new_word_set


def _extend_word_endings(text_set: set[str]) -> set[str]:
    new_set = text_set.copy()
    new_set.update(text[:-1] for text in text_set if len(text) > 4)
    new_set.update(text[:-2] for text in text_set if len(text) > 5)
    return new_set


def create_extended_word_set(text: str, nlp: Language) -> set[str]:
    word_set = _lemmatize_tokens(text, nlp)
    word_set = _lemmatize_repeatedly(word_set, nlp)
    word_set = set(word.lower() for word in word_set)
    word_set = _extend_word_endings(word_set)
    return word_set
