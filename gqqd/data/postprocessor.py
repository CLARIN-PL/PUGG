from unidecode import unidecode


class QuestionPostprocessor:
    """
    A class used to postprocess questions in the final dataset construction.
    """

    def __call__(self, question: str) -> str:
        return self._remove_crossword(question)

    def _remove_crossword(self, question: str) -> str:
        """
        Removes the word "krzyżówka" (crossword) from the question if it exists, as it is
        meaningless in our case based on the analysis.
        """
        if " krzyżówka?" not in question:
            assert " krzyzowka?" not in unidecode(question)
            return question
        else:
            return question.replace(" krzyżówka?", "?")
