import re

import numpy as np
import pandas as pd
from tinydb import TinyDB
from tqdm import tqdm

from gqqd.defaults import WIKI_RESULTS

df = pd.DataFrame(TinyDB(WIKI_RESULTS / "db.json", indent=4, ensure_ascii=False).table("results"))
df.plain_text = df.plain_text.apply(lambda x: re.sub(r"\s", " ", x))

all_links = []

for row in tqdm(df.itertuples()):
    tags = np.full(len(row.plain_text), "O", dtype=object)
    for link in row.wiki_links:
        tags[link["start_idx"] : link["end_idx"]] = link["wiki_link"]

    mask_array = np.ones(len(row.plain_text), dtype=bool)
    for match in re.finditer(r"  +", row.plain_text):
        mask_array[match.start() + 1 : match.end()] = False

    masked_tags = pd.Series(tags[mask_array])
    group_enum = masked_tags.ne(masked_tags.shift()).cumsum()
    group_beginnings = masked_tags.loc[~group_enum.duplicated()]

    index_df = pd.DataFrame(
        {
            "start_idx": group_beginnings.index,
            "end_idx": group_enum.drop_duplicates(keep="last").index + 1,
            "wiki_link": group_beginnings,
        }
    )
    index_df = index_df[index_df.wiki_link != "O"]
    links = index_df.to_dict("records")
    all_links.append(links)

df.wiki_links = all_links
df.plain_text = df.plain_text.apply(lambda x: re.sub(r"  +", " ", x))

assert not (WIKI_RESULTS / "db_fixed.json").exists()

db = TinyDB(WIKI_RESULTS / "db_fixed.json", indent=4, ensure_ascii=False)
table_results = db.table("results")
table_results.insert_multiple(df.to_dict("records"))
