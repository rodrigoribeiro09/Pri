import pandas as pd

def get_artists_missing_country(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    missing = df[(df['artist_country'].isna()) | (df['artist_country'].str.strip() == "") |
                 (df['artist_country_code'].isna()) | (df['artist_country_code'].str.strip() == "")]
    return missing

import pandas as pd

def get_bugged_bio_artists(csv_file):
    df = pd.read_csv(csv_file, dtype=str)

    if 'artist_bio' not in df.columns:
        raise ValueError("A coluna 'artist_bio' não existe no dataset!")

    patterns = [
        "tags",
        "fix your tags",
        "this is not an artist",
        "warning! deleting this artist may remove"
    ]

    regex_pattern = "|".join(patterns)

    bugged = df[
        df['artist_bio'].str.contains(regex_pattern, case=False, na=False)
    ]

    return bugged


import csv

def split_broken_rows(csv_file):
    with open(csv_file, "r", encoding="utf-8", errors="replace") as f:
        lines = list(csv.reader(f))

    header = lines[0]
    expected_cols = len(header)

    clean = []
    broken = []

    for i, row in enumerate(lines[1:], start=2):
        if len(row) == expected_cols:
            clean.append(row)
        else:
            broken.append([i, len(row)] + row)

    # Guardar linhas boas
    with open("clean_rows.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(clean)

    # Guardar linhas lixadas
    with open("broken_rows.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["line_number", "columns_found"] + header)
        writer.writerows(broken)

    print(f"Linhas OK: {len(clean)}")
    print(f"Linhas com erro: {len(broken)} (guardadas em broken_rows.csv)")

import pandas as pd

def get_default_dataset():
  
    df = pd.read_csv("dataset/dataset.csv")
    cols_to_drop = [c for c in ["artist_nationality", "song_genre"] if c in df.columns]
    df=df.drop(columns=cols_to_drop)
    df.to_csv("dataset/dataset_simple.csv", index=False)
    return 

if __name__ == "__main__":
    get_default_dataset()