import json
from pathlib import Path
from typing import Union

import tqdm
import typer
from pygaggle.rerank.base import Query, Text
from pygaggle.rerank.transformer import MonoT5


def main(
    input_path: Path = typer.Option(
        "data/datasets/suggestion_dataset/results/output/qa_for_annotation.json"
    ),
    output_path: Path = typer.Option(
        "data/datasets/suggestion_dataset/results/annotated/qa_reranked.json"
    ),
    reranker_model_name: str = typer.Option("unicamp-dl/mt5-base-mmarco-v2"),
    device: Union[str, None] = typer.Option(None),
) -> None:
    print(locals())
    with open(input_path, "r") as f:
        data = json.load(f)

    model = MonoT5.get_model(reranker_model_name, device=device)
    reranker = MonoT5(pretrained_model_name_or_path=reranker_model_name, model=model)
    print(model.device)
    print(reranker.device)

    for idx, entry in enumerate(tqdm.tqdm(data)):
        question = data[idx]["question"]
        test_q = Query(question)
        test_texts = [
            Text(context["text"], {"docid": passage_idx}, 0)
            for passage_idx, context in enumerate(data[idx]["passages"])
        ]

        reranked = reranker.rerank(test_q, test_texts)
        for rerank_result in reranked:
            passage_idx = rerank_result.metadata["docid"]
            data[idx]["passages"][passage_idx]["reranker_score"] = rerank_result.score

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


typer.run(main)
