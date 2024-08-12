import json
from collections import defaultdict
from dataclasses import asdict, dataclass

import srsly
import typer
from dotenv import load_dotenv
from tqdm import tqdm

from gqqd.api.suggestion_client import SuggestionClient
from gqqd.defaults import CREDENTIALS_ENV, QUESTION_PREFIXES, SUGGESTIONS_PATH


@dataclass
class SuggestionResult:
    query: str
    suggestions: list[str]


def main(dataset: str = typer.Option(...)):
    prefixes = set(srsly.read_json(QUESTION_PREFIXES / f"{dataset}.json"))

    results = []
    failed = defaultdict(int)
    rejected = []

    client = SuggestionClient()
    with tqdm(total=len(prefixes)) as pbar:
        while prefixes:
            prefix = prefixes.pop()
            suggestions = client.suggest(prefix)
            if suggestions is not None:
                results.append(SuggestionResult(query=prefix, suggestions=suggestions))
                pbar.update()
            else:
                failed[prefix] += 1
                if failed[prefix] < 5:
                    prefixes.add(prefix)
                else:
                    rejected.append(prefix)
                    pbar.update()
                pbar.set_postfix({"failed": sum(failed.values()), "rejected": len(rejected)})

    SUGGESTIONS_PATH.mkdir(parents=True, exist_ok=True)

    with (SUGGESTIONS_PATH / f"{dataset}.json").open("w") as f:
        json.dump([asdict(x) for x in results], f, indent=4, ensure_ascii=False)

    with (SUGGESTIONS_PATH / f"{dataset}.json_log").open("w") as f:
        json.dump(
            {
                "success": len(results) / (len(results) + len(rejected)),
                "num_rejected": len(rejected),
                "failed": failed,
                "rejected": rejected,
            },
            f,
            indent=4,
            ensure_ascii=False,
        )


load_dotenv(CREDENTIALS_ENV)
typer.run(main)
