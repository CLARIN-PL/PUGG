import json
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class SuggestionClient:
    headers = {
        "User-Agent": os.getenv("USER_AGENT")
    }

    def __init__(self) -> None:
        self.http = self.init_session()

    def suggest(self, query: str) -> list[str] | None:
        response = self.http.get(
            f"http://google.com/complete/search?client=chrome&hl=pl&gl=PL&q={query}",
            headers=self.headers,
        )

        if response.status_code != 200:
            print(f"Error {response.status_code}")
            return None

        suggestions = json.loads(response.text)[1]
        assert isinstance(suggestions, list)
        return suggestions

    def init_session(self) -> requests.Session:
        adapter = HTTPAdapter(max_retries=Retry(backoff_factor=1, total=20))
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http
