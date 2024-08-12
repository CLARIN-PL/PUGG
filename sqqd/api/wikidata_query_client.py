import http.client
import json
import time
from typing import Any, Dict, Optional, Union
from urllib.error import HTTPError

from SPARQLWrapper import JSON, SPARQLExceptions, SPARQLWrapper, __agent__


class WikidataSPARQLClient:
    object_name_retrieving_query = (
        "SELECT ?relationLabel WHERE {{ wd:{object_id} rdfs:label ?relationLabel. FILTER ("
        'lang(?relationLabel) = "pl")}}'
    )

    def __init__(
        self, max_attempts: int = 20, retry_delay_seconds: int = 60, agent: str | None = None
    ) -> None:
        self.endpoint_url = "https://query.wikidata.org/sparql"
        if agent is None:
            agent = __agent__
        self.sparql = SPARQLWrapper(self.endpoint_url, agent=agent)
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds

    def get_query_results(self, query: str, attempt: int = 0) -> Union[Dict[str, Any], None]:
        try:
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()
            if isinstance(results, dict):
                return results
            return None
        except (HTTPError, ConnectionError):
            if attempt >= self.max_attempts:
                print(f"Max attempts reached. Unable to execute query: {query}")
                return None
            else:
                print(f"Error encountered. Retrying in {self.retry_delay_seconds} seconds.")
                time.sleep(self.retry_delay_seconds)
                return self.get_query_results(query, attempt + 1)
        except (json.JSONDecodeError, http.client.IncompleteRead) as e:
            print("An error occurred while reading JSON:")
            print(e)
            return None
        except SPARQLExceptions.EndPointInternalError as e:
            print("An internal Wikidata error occurred:")
            print(e)
            return None

    def get_object_name(self, object_id: str) -> Optional[str]:
        query = self.object_name_retrieving_query.format(object_id=object_id)
        results = self.get_query_results(query)
        if results and "results" in results and "bindings" in results["results"]:
            for item in results["results"]["bindings"]:
                relation_label = str(item["relationLabel"]["value"])
                return relation_label
        return None
