import json
from itertools import product
from pathlib import Path
from typing import Iterable

import srsly
import typer
from qwikidata.entity import WikidataEntity, WikidataItem, WikidataProperty
from qwikidata.json_dump import WikidataJsonDump
from tqdm import tqdm, trange

from gqqd.defaults import FILTERED_WIKIDATA_DUMP, FINAL_DATASET_KBQA, ORIGINAL_WIKIDATA_DUMP

WIKIDATA_FILE_NAME = "wikidata-20231016-all.json.gz"
WIKIDATA_DUMP_LENGTH = 106154663


def main(
    hop: int = typer.Option(...), wikidata_dump: str = typer.Option(WIKIDATA_FILE_NAME)
) -> None:
    out_fname = FILTERED_WIKIDATA_DUMP / f"filtered_entities_hop_{hop}.json"
    entities_to_filter = load_entities_to_filter(hop)
    print(f"Number of entities to filter {len(entities_to_filter)}")

    wjd_dump_path = ORIGINAL_WIKIDATA_DUMP / wikidata_dump
    wjd = WikidataJsonDump(str(wjd_dump_path))

    extracted_entities = []
    for entity_dict in tqdm(wjd, total=WIKIDATA_DUMP_LENGTH, smoothing=0.05):
        if entity_dict["type"] in {"item", "property"}:
            if entity_dict["id"] in entities_to_filter:
                if entity_dict["type"] == "item":
                    entity = WikidataItem(entity_dict)
                else:
                    entity = WikidataProperty(entity_dict)
                extracted_entities.append(entity)

    dump_entities_to_json(extracted_entities, out_fname)


def dump_entities_to_json(entities: Iterable[WikidataEntity], out_fname: Path) -> None:
    with open(out_fname, "w") as fp:
        fp.write("[")
        ent_iter = iter(entities)
        ent = next(ent_iter, None)
        while ent:
            ent_str = json.dumps(ent._entity_dict, ensure_ascii=False)
            fp.write("\n{}".format(ent_str))
            ent = next(ent_iter, None)
            if ent:
                fp.write(",")

        fp.write("\n]")


def load_source_entities() -> set[str]:
    entities = set()
    for dataset_type, subset in product(["natural", "template-based"], ["train", "test"]):
        data = srsly.read_json(FINAL_DATASET_KBQA / f"kbqa_{dataset_type}/{subset}.json")
        for entry in data:
            for entity in entry["topic"] + entry["answer"]:
                entities.add(entity["entity_id"])

    return entities


def load_entities_to_filter(hop: int) -> set[str]:
    assert hop >= 0
    if hop == 0:
        return load_source_entities()
    elif hop > 0:
        entities_to_filter = set()
        for i in trange(hop, desc="Loading entities to filter."):
            wjd = WikidataJsonDump(str(FILTERED_WIKIDATA_DUMP / f"filtered_entities_hop_{i}.json"))
            for entity_dict in wjd:
                entities_to_filter.add(entity_dict["id"])
                if entity_dict["type"] == "item":
                    claim_groups = WikidataItem(entity_dict).get_truthy_claim_groups()
                    for p, claim_group in claim_groups.items():
                        entities_to_filter.add(p)
                        for claim in claim_group:
                            if claim.mainsnak.value_datatype == "wikibase-entityid":
                                entities_to_filter.add(claim.mainsnak.datavalue.value["id"])
        return entities_to_filter


typer.run(main)
