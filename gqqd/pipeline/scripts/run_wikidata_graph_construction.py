import json
from typing import Any

import typer
from qwikidata.entity import WikidataItem, WikidataProperty
from qwikidata.json_dump import WikidataJsonDump
from tqdm import tqdm

from gqqd.defaults import FILTERED_WIKIDATA_DUMP, ORIGINAL_WIKIDATA_DUMP, WIKIDATA_GRAPHS

WIKIDATA_FILE_NAME = "wikidata-20231016-all.json.gz"
WIKIDATA_DUMP_LENGTH = 106154663


def load_graph_data(hop: int, wikidata_dump: str | None) -> dict[str, Any]:
    triples = []
    attributes = []
    times = []
    labels_pl = {}
    labels_en = {}
    descriptions = {}
    aliases = {}
    if hop != -1:
        assert wikidata_dump is None
        wjd = WikidataJsonDump(str(FILTERED_WIKIDATA_DUMP / f"filtered_entities_hop_{hop}.json"))
        total = None
    else:
        wjd = WikidataJsonDump(str(ORIGINAL_WIKIDATA_DUMP / wikidata_dump))
        total = WIKIDATA_DUMP_LENGTH

    for entity_dict in tqdm(wjd, total=total, smoothing=0.05):
        if entity_dict["type"] == "item":
            entity = WikidataItem(entity_dict)
        else:
            entity = WikidataProperty(entity_dict)
        labels_pl[entity.entity_id] = entity.get_label("pl")
        labels_en[entity.entity_id] = entity.get_label("en")
        descriptions[entity.entity_id] = entity.get_description("pl")
        aliases[entity.entity_id] = entity.get_aliases("pl")

        if entity_dict["type"] == "item":
            claim_groups = WikidataItem(entity_dict).get_truthy_claim_groups()
            for p, group in claim_groups.items():
                for claim in group:
                    if claim.mainsnak.value_datatype == "wikibase-entityid":
                        triples.append((entity.entity_id, p, claim.mainsnak.datavalue.value["id"]))
                    elif claim.mainsnak.value_datatype == "string":
                        attributes.append((entity.entity_id, p, claim.mainsnak.datavalue.value))
                    elif claim.mainsnak.value_datatype == "time":
                        times.append((entity.entity_id, p, claim.mainsnak.datavalue.value))
    return {
        "triples": triples,
        "attributes": attributes,
        "times": times,
        "labels_pl": labels_pl,
        "labels_en": labels_en,
        "descriptions": descriptions,
        "aliases": aliases,
    }


def remove_entities_without_labels(
    triples: list[tuple[str, str, str]], labels: dict[str, str]
) -> list[tuple[str, str, str]]:
    entities = set(labels.keys())
    return [(h, r, t) for h, r, t in triples if t in entities and h in entities]


def main(
    hop: int = typer.Option(...), wikidata_dump: str | None = typer.Option(WIKIDATA_FILE_NAME)
) -> None:
    if hop != -1:
        assert hop >= 0
        wikidata_dump = None
        out_fname = WIKIDATA_GRAPHS / f"hop_{hop}"
    else:
        out_fname = WIKIDATA_GRAPHS / "all"
    graph = load_graph_data(hop, wikidata_dump)
    print(f"{len(graph['triples'])=}")
    print(f"{len(graph['attributes'])=}")
    print(f"{len(graph['times'])=}")
    print(f"{len(graph['labels_pl'])=}")
    print(f"{len(graph['labels_en'])=}")
    print(f"{len(graph['descriptions'])=}")
    print(f"{len(graph['aliases'])=}")
    graph["triples"] = remove_entities_without_labels(graph["triples"], graph["labels_pl"])
    print(f"After filtering: {len(graph['triples'])=}")

    out_fname.mkdir(exist_ok=True, parents=True)
    for k, v in graph.items():
        with open(out_fname / f"{k}.json", "w") as f:
            json.dump(v, f, ensure_ascii=False, indent=4)


typer.run(main)
