import pandas as pd
from dotenv import load_dotenv
from mpire import WorkerPool

from gqqd.api.wikidata import WikidataClient
from gqqd.data.final import get_final_df
from gqqd.defaults import ENTITY_LINKING_ANNOTATION, ROOT_PATH

N_JOBS = 20


def load_data() -> pd.DataFrame:
    df = get_final_df()

    assert df.annotation.nunique() == 2
    print(f"Number of input questions: {df.q_p_id.nunique()}")

    notes = dict(df[df.note.str.len() > 0][["q_p_id", "note"]].values)
    df["note"] = df.q_p_id.map(notes)
    positively_verified = df[df.annotation == 1].copy()
    client = WikidataClient()
    with WorkerPool(N_JOBS, start_method="threading") as pool:
        is_disambiguation_page_results = pool.map(
            client.is_disambiguation_page, positively_verified.entity_id, progress_bar=True
        )
    positively_verified["is_disambiguation_page"] = is_disambiguation_page_results
    disamb_df = positively_verified[positively_verified.is_disambiguation_page.isin([True, None])]

    print(
        f"Number of questions for manual correction (disambiguation): {disamb_df.q_p_id.nunique()}"
    )
    print(f"Number of questions for manual correction (note): {len(notes)}")

    to_manual_correction = set(notes.keys()) | set(disamb_df.q_p_id)
    to_corr_df = df[df.q_p_id.isin(to_manual_correction)].copy()
    to_corr_df["reason"] = ""
    to_corr_df.loc[to_corr_df.q_p_id.isin(notes.keys()), "reason"] = "note;"
    to_corr_df.loc[to_corr_df.q_p_id.isin(disamb_df.q_p_id), "reason"] += "disambiguation;"

    positive_ids = to_corr_df[to_corr_df.annotation == 1].q_p_id
    negative_ids = to_corr_df.q_p_id[~to_corr_df.q_p_id.isin(positive_ids)]

    positive = to_corr_df[to_corr_df.q_p_id.isin(positive_ids) & (to_corr_df.annotation == 1)]
    negative = to_corr_df[to_corr_df.q_p_id.isin(negative_ids)].drop_duplicates(subset=["q_p_id"])
    return pd.concat([positive, negative], ignore_index=True)


load_dotenv(ROOT_PATH / ".env")
data = load_data()
print(f"Number of questions for manual correction: {data.q_p_id.nunique()}")

output_dir = ENTITY_LINKING_ANNOTATION / "correction"
output_dir.mkdir(exist_ok=True, parents=True)
data.to_csv(output_dir / "to_correct.csv")
