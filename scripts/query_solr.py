#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
import glob
import requests

def edismax_query_from_config(config_path, solr_uri, collection):
    """
    Executa uma query EDisMax no Solr com base numa configuração JSON avançada.
    Trata fuzziness, wildcards, proximidade e phrase boosts de forma segura.
    """

    # === 1. Ler configuração JSON ===
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f" Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON format in config file: {config_path}")
        sys.exit(1)

    # === 2. Parâmetros da query ===
    base_query = config.get("q", "").strip()
    fuzziness_terms = config.get("fuzziness_terms", [])
    wildcard_terms = config.get("wildcard_terms", [])
    proximity_terms = config.get("proximity_terms", {})
    independent_boosts = config.get("independent_boosts", [])

    qf = config.get("qf", "")
    pf = config.get("pf", "")
    rows = config.get("rows", 10)

    # === 3. Construir query segura ===
    final_query_parts = [base_query]

    # Fuzziness
    final_query_parts += [f"{t}~1" for t in fuzziness_terms]

    # Wildcards
    final_query_parts += [f"{t}*" for t in wildcard_terms]

    # Proximity phrases (escapando aspas)
    for phrase, slop in proximity_terms.items():
        escaped_phrase = phrase.replace('"', '\\"')
        final_query_parts.append(f'"{escaped_phrase}"~{slop}')

    final_query = " ".join(final_query_parts)

    # === 4. Parâmetros Solr ===
    params = {
        "q": final_query,
        "defType": "edismax",
        "qf": qf,
        "pf": pf,
        "rows": rows,
        "wt": "json",
        "fl": "*,score"
    }

    if independent_boosts:
        params["bf"] = " ".join(independent_boosts)

    # === 5. Executar query ===
    uri = f"{solr_uri.rstrip('/')}/{collection}/select"

    try:
        response = requests.get(uri, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f" Error querying Solr: {e}")
        sys.exit(1)

    print(f"🔍 Final Solr query: {final_query}")
    return response.json()


def main(query_folder: Path, solr_uri: str, collections: list[str]):
    """
    Lê todos os ficheiros JSON num diretório, atribui cada query a uma
    collection em round-robin e guarda resultados completos e
    simplificados em dois ficheiros JSON.

    """
    sys.stdout.reconfigure(encoding='utf-8')

    query_files = sorted(glob.glob(query_folder.joinpath("*.json").as_posix()))
    if not query_files:
        print(f" No query files found in {query_folder}")
        sys.exit(1)

    results_full = {}
    results_simple = {}

    for idx, query_file in enumerate(query_files):
        filename = Path(query_file).stem
        collection = collections[idx % len(collections)] if collections else "music"
        print(f" Running query {filename} against collection: {collection} ...")

        try:
            solr_result = edismax_query_from_config(query_file, solr_uri, collection)

            # Usar o mesmo formato de output antigo: chaves inteiras quando possível
            key = int(filename)
            results_full[key] = solr_result

            # Extrair campos simples
            simple_docs = []
            for doc in solr_result.get("response", {}).get("docs", []):
                simple_doc = {
                    "id": doc.get("id"),
                    "song_name": doc.get("song_name", [""])[0] if doc.get("song_name") else "",
                    "artist_name": doc.get("artist_name", "")
                }
                simple_docs.append(simple_doc)

            results_simple[key] = {"response": {"docs": simple_docs}}

        except Exception as e:
            print(f"  Error running query {filename}: {e}")
            continue

    # Guardar resultados
    output_path_full = Path("results/solr_output.json")
    output_path_full.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path_full, "w", encoding="utf-8") as f:
        json.dump(results_full, f, indent=2, ensure_ascii=False)

    output_path_simple = Path("results/solr_output_format.json")
    with open(output_path_simple, "w", encoding="utf-8") as f:
        json.dump(results_simple, f, indent=2, ensure_ascii=False)

    print(f" Resultados completos guardados em: {output_path_full.resolve()}")
    print(f" Resultados simplificados guardados em: {output_path_simple.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run EDisMax Solr queries from JSON configs and output results in JSON format."
    )

    parser.add_argument(
        "--queries",
        type=Path,
        required=True,
        help="Path to directory containing JSON query config files.",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="Solr instance URI (default: http://localhost:8983/solr).",
    )
    parser.add_argument(
        "--collections",
        type=str,
        nargs="+",
        required=False,
        help="One or more Solr collection names. Example: --collections model1 model2 model3",
    )

    args = parser.parse_args()

    # Prefer --collections if provided, fall back to --collection for compatibility
    if args.collections:
        collections = args.collections
    else:
        collections = ["music"]

    main(args.queries, args.uri, collections)