from matplotlib.path import Path
import requests
from pathlib import Path
import json
import requests
import sys

SOLR_URL = "http://localhost:8983/solr/songs/schema"
SCHEMA_FILE = "solr/schema.xml"  

def read_json(relative_path):
    """
    Reads a JSON file from a relative path and returns it as a Python dictionary.
    
    Args:
        relative_path (str or Path): Relative path to the JSON file.
        
    Returns:
        dict: Parsed JSON content.
    """
    # Convert to Path object (relative to current working directory)
    config_file = Path(relative_path)
    
    try:
        with config_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{relative_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{relative_path}': {e}")
        return None

def parse_schema(xml_path):
    """Parse your schema.xml file and extract fieldTypes and fields."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    field_types = []
    fields = []

    # Parse fieldTypes
    for ft in root.findall("fieldType"):
        analyzer_elem = ft.find("analyzer")
        if analyzer_elem is not None:
            # Build analyzer dict manually
            tokenizer = analyzer_elem.find("tokenizer")
            filters = analyzer_elem.findall("filter")
            field_types.append({
                "name": ft.get("name"),
                "class": ft.get("class"),
                "positionIncrementGap": ft.get("positionIncrementGap", "100"),
                "analyzer": {
                    "tokenizer": {"class": tokenizer.get("class")},
                    "filters": [
                        {k: v for k, v in f.items()} for f in filters
                    ]
                }
            })
        else:
            field_types.append({k: v for k, v in ft.items()})

    # Parse fields
    for f in root.findall("field"):
        fields.append({
            "name": f.get("name"),
            "type": f.get("type"),
            "stored": f.get("stored") == "true",
            "indexed": f.get("indexed") == "true",
        })

    return field_types, fields


def add_to_solr(field_types, fields):
    """Send field types and fields to Solr via Schema API."""
    for ft in field_types:
        r = requests.post(SOLR_URL, json={"add-field-type": ft})
        print(f"Added field type '{ft['name']}': {r.status_code} - {r.text}")

    for f in fields:
        r = requests.post(SOLR_URL, json={"add-field": f})
        print(f"Added field '{f['name']}': {r.status_code} - {r.text}")


SOLR_URL = "http://localhost:8983/solr/songs/select"

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
        "wt": "json"
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

if __name__ == "__main__":

    config = read_json("../queries/heartBreak/simple.json")  # relative path~
    edismax_query_from_config(config)
    



def main():
    field_types, fields = parse_schema(SCHEMA_FILE)
    add_to_solr(field_types, fields)
    print("✅ Schema upload completed!")



