import os
from pathlib import Path

TEMPLATE_LIST = [
    "one_hop_template",
    "one_hop_template_with_mask",
    "two_hop_template",
    "reverse_one_hop_template",
    "reverse_one_hop_template_with_mask",
    "reverse_two_hop_template",
    "reverse_two_hop_template_with_mask",
    "mixed_template",
]

ROOT_PATH = Path(os.path.dirname(__file__)).parent.absolute()
DATA_PATH = ROOT_PATH / "data"

ENTITIES_PATH = DATA_PATH / "datasets/sparql_dataset/entities"
PROPERTIES_PATH = DATA_PATH / "datasets/sparql_dataset/properties"
VITAL_ARTICLES_PATH = DATA_PATH / "datasets/sparql_dataset/vital_articles"
SPARQL_QUESTIONS = DATA_PATH / "datasets/sparql_dataset/sparql_questions"
CHATGPT_INFLECTION_RESULTS = DATA_PATH / "datasets/sparql_dataset/chatgpt_inflection_results"
CHATGPT_PARAPHRASE_RESULTS = DATA_PATH / "datasets/sparql_dataset/chatgpt_paraphrase_results"
OUTPUT_PATH = DATA_PATH / "datasets/sparql_dataset/output"
ANNOTATION_PATH = DATA_PATH / "datasets/sparql_dataset/annotation"

CHATGPT_INFLECTION_CONFIG = (
    ROOT_PATH / "sqqd/api/chatgpt_rephrasing/chatgpt_config_for_inflection.yaml"
)
CHATGPT_PARAPHRASE_CONFIG = (
    ROOT_PATH / "sqqd/api/chatgpt_rephrasing/chatgpt_config_for_paraphrasing.yaml"
)
