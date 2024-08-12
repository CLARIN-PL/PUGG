import os
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.absolute()
DATA_PATH = ROOT_PATH / "data"

CZYWIESZ_DATASET_PATH = DATA_PATH / "datasets/external/czywiesz"
POQUAD_DATASET_PATH = DATA_PATH / "datasets/external/poquad"
QUESTION_PREFIXES = DATA_PATH / "datasets/suggestion_dataset/prefixes"
SUGGESTIONS_PATH = DATA_PATH / "datasets/suggestion_dataset/suggestions"
SEARCH_RESULTS = DATA_PATH / "datasets/suggestion_dataset/search_results"
CORRECT_PREFIXES = DATA_PATH / "datasets/suggestion_dataset/filtering/correct_prefixes"
WIKI_RESULTS = DATA_PATH / "datasets/suggestion_dataset/wiki_content"
WIKIDATA_ITEM_IDS = DATA_PATH / "datasets/suggestion_dataset/wikidata_item_ids"
OUTPUT_PATH = DATA_PATH / "datasets/suggestion_dataset/results/output"
ANNOTATED_PATH = DATA_PATH / "datasets/suggestion_dataset/results/annotated"
ENTITY_LINKING_INPUT = DATA_PATH / "datasets/suggestion_dataset/entity_linking/input"
ENTITY_LINKING_PROCESSED = DATA_PATH / "datasets/suggestion_dataset/entity_linking/processed"
ENTITY_LINKING_OUTPUT = DATA_PATH / "datasets/suggestion_dataset/entity_linking/output"
ENTITY_LINKING_ANNOTATION = DATA_PATH / "datasets/suggestion_dataset/entity_linking/annotation"
INFOREX_OUTPUT_VERIFICATION = (
    DATA_PATH / "datasets/suggestion_dataset/results/annotated/inforex_output_verification"
)

FINAL_GQQD_DATASET = DATA_PATH / "datasets/suggestion_dataset/final"
FINAL_DATASET = DATA_PATH / "datasets/final"
FINAL_DATASET_KBQA = FINAL_DATASET / "kbqa"
FINAL_DATASET_MRC = FINAL_DATASET / "mrc"
FINAL_DATASET_IR = FINAL_DATASET / "ir"

WIKIDATA_DUMPS = DATA_PATH / "wikidata/dumps"
ORIGINAL_WIKIDATA_DUMP = WIKIDATA_DUMPS / "original"
FILTERED_WIKIDATA_DUMP = WIKIDATA_DUMPS / "filtered"
WIKIDATA_GRAPHS = DATA_PATH / "wikidata/graphs"

CREDENTIALS_ENV = ROOT_PATH / "credentials.env"
CHATGPT_CONFIG = ROOT_PATH / "gqqd/auto_annotation/quote_chatgpt_config.yaml"

POSTPROCESSING_FILES = DATA_PATH / "datasets/suggestion_dataset/postprocessing"

IR_DATASET_PATH = DATA_PATH / "datasets/ir_dataset"
MRC_DATASET_PATH = DATA_PATH / "datasets/mrc_dataset"

IR_RESULTS_PATH = DATA_PATH / "baselines/ir"
MRC_RESULTS_PATH = DATA_PATH / "baselines/mrc"

HF_DATASETS_PATH = DATA_PATH / "datasets/huggingface"
DATASET_CARD_TEMPLATE = HF_DATASETS_PATH / "readme/README_dataset.md"
KG_CARD_TEMPLATE = HF_DATASETS_PATH / "readme/README_kg.md"
