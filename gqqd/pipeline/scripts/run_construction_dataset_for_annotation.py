import dataclasses
import json
from pathlib import Path

import dvc.api
import pandas as pd
import typer
from rich import print

from gqqd.data.loaders import get_search_results_df, get_suggestions_df, load_wiki_content_df
from gqqd.defaults import OUTPUT_PATH
from gqqd.pipeline.output.data import Example, Passage
from gqqd.pipeline.passage_retrieval import PassageConstructor
from gqqd.pipeline.question_filtering import (
    PrefixCorrectFilter,
    SequentialFilter,
    WikipediaInSearchExistenceFilter,
)

PARAMS = dvc.api.params_show()["construct_dataset_for_annotation"]


def main(output_filepath: Path = typer.Option(OUTPUT_PATH / "qa_for_annotation.json")) -> None:
    suggestions, search_results, executed_queries, wiki_content, acquired_wiki_pages = load_data()

    suggestions = drop_duplications(suggestions)
    suggestions = drop_not_executed(suggestions, executed_queries)

    suggestions = join_wiki_pages_column(suggestions, search_results)
    suggestions = drop_not_acquired_wiki_pages(suggestions, acquired_wiki_pages)

    suggestions = filter_question(suggestions, search_results)

    add_passages_column(suggestions, wiki_content, PARAMS["passage_length"], PARAMS["passage_step"])

    save(suggestions, output_filepath)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, set[str], pd.DataFrame, set[str]]:
    suggestions = get_suggestions_df()
    print(f"Found {len(suggestions)} suggestions.")
    search_results = get_search_results_df()
    executed_queries = set(search_results["query"].unique())
    assert len(search_results) == len(executed_queries)
    print(f"Found {len(executed_queries)} executed queries.")
    wiki_content = load_wiki_content_df()
    acquired_wiki_pages = set(wiki_content["page"].unique())
    assert len(wiki_content) == len(acquired_wiki_pages)
    print(f"Found {len(acquired_wiki_pages)} wiki contents.")
    return suggestions, search_results, executed_queries, wiki_content, acquired_wiki_pages


def drop_duplications(suggestions: pd.DataFrame) -> pd.DataFrame:
    unique_suggestions = suggestions.drop_duplicates(["suggestions"])
    print(f"Dropped {len(suggestions) - len(unique_suggestions)} suggestions due to duplications.")
    return unique_suggestions


def drop_not_executed(suggestions: pd.DataFrame, executed_queries: set[str]) -> pd.DataFrame:
    executed_suggestions = suggestions[
        suggestions.suggestions.apply(lambda x: x in executed_queries)
    ]
    print(
        f"Dropped {len(suggestions) - len(executed_suggestions)} suggestions due to lack of "
        "executed queries."
    )
    return executed_suggestions


def join_wiki_pages_column(suggestions: pd.DataFrame, search_results: pd.DataFrame) -> pd.DataFrame:
    joined = (
        suggestions.set_index("suggestions")
        .join(search_results.set_index("query"))
        .reset_index()[list(suggestions.columns) + ["wiki_pages"]]
    )
    assert len(suggestions) == len(joined)
    return joined


def drop_not_acquired_wiki_pages(
    suggestions: pd.DataFrame, acquired_wiki_pages: set[str]
) -> pd.DataFrame:
    content_acquired_suggestions = suggestions[
        suggestions.wiki_pages.apply(
            lambda pages: all(page in acquired_wiki_pages for page in pages)
        )
    ]
    print(
        f"Dropped {len(suggestions) - len(content_acquired_suggestions)} suggestions due "
        "to lack of wiki contents."
    )
    return content_acquired_suggestions


def filter_question(suggestions: pd.DataFrame, search_results: pd.DataFrame) -> pd.DataFrame:
    question_filter = SequentialFilter(
        [PrefixCorrectFilter(), WikipediaInSearchExistenceFilter(search_results)]
    )
    correct_suggestions = suggestions[suggestions.suggestions.apply(question_filter.is_ok)]
    print(f"Filtered out {len(suggestions) - len(correct_suggestions)} suggestions.")
    return correct_suggestions


def add_passages_column(
    suggestions: pd.DataFrame, wiki_content: pd.DataFrame, length: int, step: int
) -> None:
    constructor = PassageConstructor(length, step)
    passages = []
    for row in suggestions.itertuples():
        row_passages = []
        for page in row.wiki_pages:
            [content_row] = wiki_content[wiki_content.page == page].iloc
            row_passages += [
                Passage(wiki_page=page, text=passage, links=links, time_acquired=content_row.time)
                for passage, links in zip(
                    *constructor.construct(content_row.plain_text, content_row.wiki_links)
                )
            ]
        passages.append(row_passages)
    suggestions["passages"] = passages


def save(suggestions: pd.DataFrame, output_filepath: Path) -> None:
    original_suggestions = get_suggestions_df()
    suggestion_dataset_mapping = original_suggestions.groupby("suggestions")["dataset"].apply(
        lambda x: list(set(x))
    )
    suggestion_prefix_mapping = original_suggestions.groupby("suggestions")["query"].apply(
        lambda x: list(set(x))
    )

    output = []
    for item in suggestions.sample(frac=1.0, random_state=7312).itertuples():
        example = Example(
            question=item.suggestions + "?",
            answer=None,
            passages=item.passages,
            prefix=suggestion_prefix_mapping[item.suggestions],
            prefix_from=suggestion_dataset_mapping[item.suggestions],
        )
        output.append(example)

    assert len(set(x.id for x in output)) == len(output)

    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    with output_filepath.open("w") as f:
        json.dump(
            [dataclasses.asdict(example) for example in output],
            f,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Saved {len(output)} examples as output dataset in {OUTPUT_PATH}.")


typer.run(main)
