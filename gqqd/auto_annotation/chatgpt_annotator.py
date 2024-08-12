import os
from difflib import SequenceMatcher
from typing import Any

import openai
import spacy
from dotenv import load_dotenv

from gqqd.defaults import ROOT_PATH


class ChatGPTClient:
    def __init__(self, messages: list[dict[str, str]], final_message_schema: str):
        self.messages = messages
        self.final_message_schema = final_message_schema

        if (ROOT_PATH / "credentials.env").exists():
            load_dotenv(ROOT_PATH / "credentials.env")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_response(self, question: str, context: str) -> tuple[str, dict[str, Any]]:
        messages = self.messages.copy()
        messages.append(
            {
                "role": "user",
                "content": self.final_message_schema.format(question=question, context=context),
            }
        )

        model = "gpt-3.5-turbo"

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        return response["choices"][0]["message"]["content"], response


class ChatGPTAnnotator:
    """
    Annotator that uses ChatGPT as QA model.
    Example usage:

    config = srsly.read_yaml("quote_chatgpt_config.yaml")
    pprint(config["messages"])
    annotator = ChatGPTClient(config["messages"], config["final_message_schema"])
    text_result = annotator.get_response(
            question="kto był najbardziej wykształcony w średniowieczu?",
            context="stanów == Wyodrębnienie się stanów nastąpiło w pełnym średniowieczu (około XIII "
            "wieku). Najpierw nastąpiło na zachodzie kontynentu, a nieco później na wschodzie. "
            "Wynikło z ustabilizowania się swoistej sytuacji prawnej członków każdego stanu. "
            "Duchowieństwo jako pierwsze, za nim rycerstwo i mieszczaństwo uzyskały "
            "charakterystyczne przywileje; tym różniły się od nieposiadającego przywilejów "
            "chłopstwa. === Duchowieństwo === Na początku XIII wieku duchowni otrzymali swobodę "
            "uchylania się od norm świeckiego prawa zwyczajowego i podlegania przepisom prawa "
            "kanonicznego. Zaczęło funkcjonować oddzielne sądownictwo, a monarchowie nadawali "
            "Kościołowi liczne przywileje immunitetowe. Hierarchia kościelna (biskupi, opaci, "
            "prałaci) wywodziła się z wyższego rycerstwa, natomiast większość prezbiterów – z "
            "mieszczaństwa i chłopstwa. === Rycerstwo === Powstawało dłużej, niż duchowieństwo, "
            "i ostatecznie wykrystalizowało się pod koniec średniowiecza jako grupa adresatów "
            "licznych przywilejów",
        )[0]
    """

    def __init__(self) -> None:
        self.nlp = spacy.load("pl_core_news_lg", disable=["tagger", "parser", "ner"])

    def get_annotation_standard(self, gpt_message: str, context: str) -> dict[str, Any]:
        gpt_message_cleaned = gpt_message.lower()[: gpt_message.rfind('"')]
        string2 = gpt_message_cleaned
        string1 = context.lower()
        match = SequenceMatcher(None, string1, string2).find_longest_match(
            0, len(string1), 0, len(string2)
        )
        match_frac = match.size / len(gpt_message_cleaned)
        return {
            "gpt_answer": context[match.a : match.a + match.size],
            "span": (match.a, match.a + match.size),
            "match_frac": match_frac,
        }

    def get_annotation_lemma(self, gpt_message: str, context: str) -> dict[str, Any]:
        gpt_message_cleaned = gpt_message.lower()[: gpt_message.rfind('"')]
        string2 = gpt_message_cleaned
        string1 = context

        d1, d2 = self.nlp(string1), self.nlp(string2)

        d1_lemma = [token.lemma_.lower() for token in d1]
        d2_lemma = [token.lemma_.lower() for token in d2]

        match = SequenceMatcher(None, d1_lemma, d2_lemma).find_longest_match(
            0, len(d1_lemma), 0, len(d2_lemma)
        )
        answer = d1[match.a : match.a + match.size].text
        match_frac = len(answer) / len(gpt_message_cleaned)
        return {
            "gpt_answer": answer,
            "span": (context.find(answer), context.find(answer) + len(answer)),
            "match_frac": match_frac,
        }

    def get_annotation(self, gpt_message: str, context: str) -> dict[str, Any] | None:
        annotation_standard = self.get_annotation_standard(gpt_message, context)
        annotation_lemma = self.get_annotation_lemma(gpt_message, context)
        if (
            annotation_standard["match_frac"] >= 0.5
            and annotation_standard["match_frac"] >= annotation_lemma["match_frac"]
        ):
            return annotation_standard
        elif (
            annotation_lemma["match_frac"] >= 0.5
            and annotation_lemma["match_frac"] >= annotation_standard["match_frac"]
        ):
            return annotation_lemma
        else:
            return None
