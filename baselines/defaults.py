import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.absolute()

BASELINES_DATA_PATH = ROOT_PATH / "data/baselines"
KBQA_BASELINES_PATH = BASELINES_DATA_PATH / "kbqa"
KBQA_EMBEDDINGS_PATH = KBQA_BASELINES_PATH / "embeddings"
KBQA_PROMPT_CONFIGS_DIR = ROOT_PATH / "baselines/kbqa"
KBQA_RESULTS_PATH = KBQA_BASELINES_PATH / "results"
