#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

cores = [
    {"core": "songs", "schema": "solr/schema1.xml", "url": "http://localhost:8983/solr/songs/schema"},
    {"core": "songsBoost", "schema": "solr/schema2.xml", "url": "http://localhost:8983/solr/songsBoost/schema"},
]



def parse_schema(xml_path):
    """Parse schema.xml and extract fieldTypes and fields for Solr API."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    field_types = []
    fields = []

    for ft in root.findall("fieldType"):
        ft_data = {
            "name": ft.get("name"),
            "class": ft.get("class"),
            "positionIncrementGap": ft.get("positionIncrementGap", "100")
        }

        for analyzer_elem in ft.findall("analyzer"):
            analyzer_type = analyzer_elem.get("type")
            tokenizer = analyzer_elem.find("tokenizer")
            filters = analyzer_elem.findall("filter")
            analyzer_json = {
                "tokenizer": {"class": tokenizer.get("class")} if tokenizer is not None else None,
                "filters": [{k: v for k, v in f.items()} for f in filters]
            }
            if analyzer_type == "index":
                ft_data["indexAnalyzer"] = analyzer_json
            elif analyzer_type == "query":
                ft_data["queryAnalyzer"] = analyzer_json
            else:
                ft_data["analyzer"] = analyzer_json 

        field_types.append(ft_data)

    for f in root.findall("field"):
        fields.append({
            "name": f.get("name"),
            "type": f.get("type"),
            "stored": f.get("stored") == "true",
            "indexed": f.get("indexed") == "true",
        })

    return field_types, fields


def add_to_solr(solr_url, field_types, fields):
    """Send field types and fields to Solr via Schema API."""
    for ft in field_types:
        r = requests.post(solr_url, json={"add-field-type": ft})
        print(f"[{solr_url}] Added field type '{ft['name']}': {r.status_code} - {r.text}")

    for f in fields:
        r = requests.post(solr_url, json={"add-field": f})
        print(f"[{solr_url}] Added field '{f['name']}': {r.status_code} - {r.text}")


def parse_all():
    for entry in cores:
        print(f"Processing core '{entry['core']}' with schema '{entry['schema']}'...")
        field_types, fields = parse_schema(entry["schema"])
        add_to_solr(entry["url"], field_types, fields)


def parse_one(entry):
    print(f"Processing core '{entry['core']}' with schema '{entry['schema']}'...")
    field_types, fields = parse_schema(entry["schema"])
    add_to_solr(entry["url"], field_types, fields)


if __name__ == "__main__":
    parse_all()


