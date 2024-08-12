import os

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class WikidataClient:
    def __init__(self) -> None:
        self.http = self._init_session()
        # for this api endpoint we use the same user agent as in SPARQL endpoint
        self.sparql_user_agent = os.getenv("SPARQL_USER_AGENT", None)
        self.wikipedia_api_url = "https://pl.wikipedia.org/w/api.php"
        self.wikidata_api_url = "https://www.wikidata.org/w/api.php"

    def _init_session(self) -> requests.Session:
        adapter = HTTPAdapter(
            max_retries=Retry(
                backoff_factor=1,
                total=20,
                status_forcelist=Retry.RETRY_AFTER_STATUS_CODES | {403, 500},
            )
        )
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http

    def get_wikidata_id(self, page_title: str) -> str | None:
        params = {
            "action": "query",
            "prop": "pageprops",
            "ppprop": "wikibase_item",
            "redirects": "1",
            "format": "json",
            "titles": page_title,
        }

        response = self.http.get(self.wikipedia_api_url, params=params)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        item = pages.get(next(iter(pages), "-1"), {}).get("pageprops", {})
        return str(item.get("wikibase_item"))

    def is_disambiguation_page(self, entity_id: str) -> bool | None:
        params = {"action": "wbgetentities", "format": "json", "ids": entity_id, "props": "claims"}
        response = self.http.get(self.wikidata_api_url, params=params, headers=self.sparql_header)
        response.raise_for_status()
        data = response.json()

        # Check if the entity is a disambiguation page
        try:
            if "claims" in data["entities"][entity_id]:
                if "P31" in data["entities"][entity_id]["claims"]:
                    for claim in data["entities"][entity_id]["claims"]["P31"]:
                        if (
                            claim["mainsnak"]["datavalue"]["value"]["id"] == "Q4167410"
                        ):  # Q4167410 represents disambiguation page
                            return True
        except KeyError:
            return None

        return False

    @property
    def sparql_header(self) -> dict[str, str] | None:
        if self.sparql_user_agent is not None:
            sparql_header = {"User-Agent": self.sparql_user_agent}
        else:
            sparql_header = None
        return sparql_header
