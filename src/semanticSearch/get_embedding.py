import sys
import json
from sentence_transformers import SentenceTransformer
import pandas as pd

DATASET_FILE = "dataset/song.csv"
# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    docs = []
    print("Generating embeddings...")

    for _, row in df.iterrows():
        song_id = row.get("song_id")
        lyrics = row.get("song_lyrics", "") or ""
        embedding = model.encode(lyrics, convert_to_tensor=False).tolist()
        print(f"Generated embedding for song ID {song_id},{embedding[:5]}...")

        doc = {
            "song_id": song_id,
            "song_name": row.get("song_name", ""),
            "album_name": row.get("album_name", ""),
            "song_lyrics": lyrics,
            "artist_id": row.get("artist_id", ""),
            "vector": embedding
        }
        docs.append(doc)
    return docs

def save_json(docs, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=4, ensure_ascii=False)
    print(f"JSON com embeddings salvo em {output_file}")


if __name__ == "__main__":

    docs = generate_embeddings(DATASET_FILE)

    json_file = "dataset/dataset_with_embeddings.json"
    save_json(docs, json_file)

