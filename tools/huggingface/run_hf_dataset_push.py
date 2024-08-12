from pathlib import Path
from typing import Optional

import typer
from huggingface_hub import HfApi

from gqqd.defaults import HF_DATASETS_PATH


def main(
    dataset: Path = typer.Option(...),
    repo_id: Optional[str] = typer.Option(...),
    branch: Optional[str] = typer.Option(None, help="Branch to push the dataset to"),
) -> None:
    api = HfApi()
    api.upload_folder(
        folder_path=HF_DATASETS_PATH / dataset,
        repo_id=repo_id,
        repo_type="dataset",
        revision=branch,
        delete_patterns="*",
    )


if __name__ == "__main__":
    typer.run(main)
