from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AllKeysUsed(Exception):
    def __init__(self) -> None:
        super().__init__("All api keys were used.")


class GoogleSearchResultsClient:
    def __init__(self, api_keys: list[str], custom_search_id: str):
        assert isinstance(api_keys, list) and len(api_keys)
        self.api_keys = api_keys
        self.api_keys_iter = api_keys.__iter__()
        self.custom_search_id = custom_search_id
        self._build_next_custom_search()

    def search(self, search_term: str, num: int, **kwargs: Any) -> dict[str, Any]:
        try:
            return self._get_result(search_term, num, **kwargs)
        except HttpError as e:
            if e.status_code == 429:
                self._build_next_custom_search()
                return self.search(search_term, num, **kwargs)
            else:
                raise e

    def _get_result(self, search_term: str, num: int, **kwargs: Any) -> dict[str, Any]:
        result = self.custom_search.list(
            q=search_term, cx=self.custom_search_id, lr="lang_pl", num=num, **kwargs
        ).execute()
        assert isinstance(result, dict)
        assert isinstance(result["items"], list)
        return result

    def _build_next_custom_search(self) -> None:
        try:
            print("Building next custom search_results...")
            self.custom_search = build(
                "customsearch", "v1", developerKey=self.api_keys_iter.__next__(), num_retries=5
            ).cse()
        except StopIteration:
            raise AllKeysUsed
