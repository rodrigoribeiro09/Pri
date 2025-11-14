#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import glob
import requests

def edismax_query_from_config(config_path, solr_uri):
    """
    Execute an EDisMax query in Solr based on a JSON configuration.
    Supports simple queries or enhanced queries with qf/pf/pf2/pf1/ps/mm/tie.
    The core is taken from the 'core' attribute in the config.
    """
    # === 1. Read JSON config ===
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON format in config file: {config_path}")
        sys.exit(1)

    # === 2. Base query ===
    base_query = config.get("q", "").strip()
    query_config_type = config.get("queryConfig", "simple")  # 'simple' or 'enhanced'
    core = config.get("core", "music")  # default core if not specified
    rows = config.get("rows", 10)

    # === 3. Build query parameters ===
    params = {
        "q": base_query,
        "qf": "song_lyrics song_name artist_name artist_bio album_name",
        "defType": "edismax",
        "rows": rows,
        "wt": "json",
        "fl": "*,score"
    }

    if query_config_type == "enhanced":
        # Apply the enhanced EDisMax configuration
        params.update({
            "qf": "song_lyrics^5 song_name^3 artist_name^2 artist_bio^2 album_name^1",
            "pf": "song_lyrics^10 song_name^5",
            "pf2": "song_lyrics^7 song_name^3 artist_bio^1",
            "pf1": "song_lyrics^2 song_name^1 artist_bio^1",
            "ps": 3,
            "ps2": 2,
            "mm": "75%",
            "tie": 0.1
        })

    # === 4. Execute query against the specified core ===
    uri = f"{solr_uri.rstrip('/')}/{core}/select"

    try:
        response = requests.get(uri, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error querying Solr core '{core}': {e}")
        sys.exit(1)

    print(f"🔍 Core: {core} | Final Solr query: {base_query}")
    return response.json()


def main():
    """
    Reads all JSON query configs in a 'queries' folder,
    executes each query in its specified core,
    and writes both full and simplified results to JSON files.
    """
    sys.stdout.reconfigure(encoding='utf-8')

    query_folder = Path("./config/queries")
    solr_uri = "http://localhost:8983/solr"

    query_files = sorted(glob.glob(query_folder.joinpath("*.json").as_posix()))
    if not query_files:
        print(f"No query files found in {query_folder}")
        sys.exit(1)

    results_full = {}
    results_simple = {}
    fields_to_list = ["song_name", "song_lyrics", "album_name", "artist_name", "artist_bio"]

    for idx, query_file in enumerate(query_files):
        filename = Path(query_file).stem
        print(f"Running query {filename} ...")

        try:
            solr_result = edismax_query_from_config(query_file, solr_uri)

            # Normalize certain fields to always be lists
            for doc in solr_result.get("response", {}).get("docs", []):
                for f in fields_to_list:
                    if f in doc and not isinstance(doc[f], list):
                        doc[f] = [doc[f]]

            # Use integer key if possible
            try:
                key = int(filename)
            except ValueError:
                key = filename

            results_full[key] = solr_result

            # Extract simplified docs
            simple_docs = []
            for doc in solr_result.get("response", {}).get("docs", []):
                simple_doc = {
                    "id": doc.get("id"),
                    "song_name": doc.get("song_name", []),
                    "artist_name": doc.get("artist_name", [])
                }
                simple_docs.append(simple_doc)

            results_simple[key] = {"response": {"docs": simple_docs}}

        except Exception as e:
            print(f"Error running query {filename}: {e}")
            continue

    # Save results
    output_path_full = Path("results/solr_output.json")
    output_path_full.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path_full, "w", encoding="utf-8") as f:
        json.dump(results_full, f, indent=2, ensure_ascii=False)

    output_path_simple = Path("results/solr_output_format.json")
    with open(output_path_simple, "w", encoding="utf-8") as f:
        json.dump(results_simple, f, indent=2, ensure_ascii=False)

    print(f"Full results saved at: {output_path_full.resolve()}")
    print(f"Simplified results saved at: {output_path_simple.resolve()}")


if __name__ == "__main__":
    main()
