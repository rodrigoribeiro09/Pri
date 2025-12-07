

import json
import pandas as pd

def build_dataset(
    songs_csv: str,
    artists_csv: str,
    out_csv: str = "dataset.csv",
):
    songs = pd.read_csv(songs_csv, dtype=str)
    artists = pd.read_csv(artists_csv, dtype=str)

    merged = pd.merge(
        songs,
        artists,
        on="artist_id",
        how="inner",
        suffixes=("", "_artist"),
    )

    dataset = merged[
        [
            "song_id",
            "song_name",
            "song_lyrics",
            "album_name",
            "genre_primary",
            "artist_name",
            "artist_bio",
            "artist_country",
        ]
    ].rename(
        columns={
            "song_id": "id",
            "genre_primary": "song_genre",
            "artist_country": "artist_nationality",
        }
    )

    dataset.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"Saved dataset to {out_csv}")


EMB_JSON = "dataset/dataset_with_embeddings.json"
OUT_JSON = "dataset/boosted.json"
DATASET_FILE = "dataset/dataset.csv"


def build_boosted_json():
    df = pd.read_csv(DATASET_FILE, dtype=str)

    with open(EMB_JSON, "r", encoding="utf-8") as f:
        embs = json.load(f)

    emb_df = pd.DataFrame(embs)

    df["id"] = df["id"].astype(str)
    emb_df["song_id"] = emb_df["song_id"].astype(str)

    emb_df = emb_df[["song_id", "vector"]]

    merged = df.merge(emb_df, left_on="id", right_on="song_id", how="inner")

    merged = merged.drop(columns=["song_id"])

    docs = merged.to_dict(orient="records")

    for d in docs:
        if isinstance(d["vector"], str):
            d["vector"] = json.loads(d["vector"])

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)

    print(f"Saved {len(docs)} docs to {OUT_JSON}")

if __name__ == "__main__":

    build_boosted_json()