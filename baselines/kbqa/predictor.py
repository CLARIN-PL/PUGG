import os
from typing import Any

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential


class GPTClient:
    def __init__(self, messages: list[dict[str, str]], final_message_schema: str, model: str):
        self.messages = messages
        self.final_message_schema = final_message_schema
        self.model = model

        openai.api_key = os.getenv("OPENAI_API_KEY")

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(20))
    def get_response(self, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        messages = self.messages.copy()
        messages.append(
            {
                "role": "user",
                "content": self.final_message_schema.format(**kwargs),
            }
        )
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )

        return response["choices"][0]["message"]["content"], response
