#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
import glob
import requests


def edismax_query_from_config(config_path, solr_uri, collection):
    """
    Faz uma query EDisMax no Solr a partir de uma configuração JSON avançada.

    Arguments:
    - config_path: caminho para o ficheiro JSON de configuração.
    - solr_uri: URL base do Solr (ex: http://localhost:8983/solr)
    - collection: nome da coleção Solr (ex: 'music')

    Retorna:
    - Dicionário JSON no mesmo formato que Solr devolve:
      {
        "response": {
          "numFound": 10,
          "docs": [{"id": "...", "score": ...}, ...]
        }
      }
    """

    # === 1. Ler ficheiro de configuração ===
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f" Config file not found: {config_path}")
        sys.exit(1)

    # === 2. Extrair parâmetros da config ===
    terms = config.get("terms", [])
    term_boosts = config.get("term_boosts", {})
    fuzziness_terms = set(config.get("fuzziness_terms", []))
    wildcard_terms = set(config.get("wildcard_terms", []))
    proximity_terms = config.get("proximity_terms", {})
    independent_boosts = config.get("independent_boosts", [])

    query_parts = []

    # === 3. Construir a query string ===
    for term in terms:
        boost = term_boosts.get(term, 1)

        # Proximity match com slop definido
        if term in proximity_terms:
            slop = proximity_terms[term]
            query_parts.append(f'"{term}"~{slop}^{boost}')
        # Frases genéricas
        elif " " in term:
            query_parts.append(f'"{term}"~2^{boost}')
        # Termos únicos com fuzziness/wildcard
        else:
            parts = []
            if term in fuzziness_terms:
                parts.append(f"{term}~1^{boost}")
            if term in wildcard_terms:
                parts.append(f"{term}*^{boost}")
            if not parts:
                parts.append(f"{term}^{boost}")
            query_parts.extend(parts)

    query_string = " OR ".join(query_parts)

    # Boost functions (bf)
    bf = " ".join(independent_boosts) if independent_boosts else None

    params = {
    "q": query_string,
    "defType": "edismax",
    "qf": config.get("qf", ""),
    "pf": config.get("pf", ""),
    "rows": config.get("rows", 10),
    "wt": "json",
    "fl": "*,score"   
    }
    if bf:
        params["bf"] = bf

    # === 4. Enviar query ao Solr ===
    uri = f"{solr_uri}/{collection}/select"
    try:
        response = requests.get(uri, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f" Error querying Solr: {e}")
        sys.exit(1)

    # === 5. Retornar JSON no formato do Solr ===
    return response.json()


def main(query_folder: Path, solr_uri: str, collection: str):
    """
    Lê todos os ficheiros JSON num diretório, executa queries EDisMax em Solr
    e imprime o resultado combinado em JSON.
    """
    sys.stdout.reconfigure(encoding='utf-8')

    results_full = {}
    results_simple = {}

    for query_file in glob.glob(query_folder.joinpath("*.json").as_posix()):
        filename = Path(query_file).stem
        print(f" Running query {filename} ...")

        try:
            solr_result = edismax_query_from_config(query_file, solr_uri, collection)
            results_full[int(filename)] = solr_result

            simple_docs = []
            for doc in solr_result.get("response", {}).get("docs", []):
                simple_doc = {
                    "id": doc.get("id"),
                    "song_name": doc.get("song_name", [""])[0] if doc.get("song_name") else "",
                    "artist_name": doc.get("artist_name", "")
                }
                simple_docs.append(simple_doc)

            results_simple[int(filename)] = {"response": {"docs": simple_docs}}

        except Exception as e:
            print(f"  Error running query {filename}: {e}")
            continue

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
        "--collection",
        type=str,
        default="music",
        help="Solr collection name (default: 'music').",
    )

    args = parser.parse_args()
    main(args.queries, args.uri, args.collection)
