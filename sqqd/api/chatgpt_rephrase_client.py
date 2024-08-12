import os

import openai
from dotenv import load_dotenv

from sqqd.defaults import ROOT_PATH


class ChatGPTClient:
    def __init__(self, messages: list[dict[str, str]]):
        self.messages = messages

        if (ROOT_PATH / "credentials.env").exists():
            load_dotenv(ROOT_PATH / "credentials.env")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_response(self, question: str) -> str:
        messages = self.messages.copy()
        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        model = "gpt-3.5-turbo"

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        return str(response["choices"][0]["message"]["content"])
