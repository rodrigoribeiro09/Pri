#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Define cores, schemas e URLs
cores = [
    {"core": "songs",  "schema": "solr/schema0.xml", "url": "http://localhost:8983/solr/songs/schema"},
    {"core": "songs1", "schema": "solr/schema1.xml", "url": "http://localhost:8983/solr/songs1/schema"},
    {"core": "songs2", "schema": "solr/schema2.xml", "url": "http://localhost:8983/solr/songs2/schema"},
    {"core": "songs3", "schema": "solr/schema3.xml", "url": "http://localhost:8983/solr/songs3/schema"},
]

def parse_schema(xml_path):
    """Parse schema.xml and extract fieldTypes and fields."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    field_types = []
    fields = []

    # Parse fieldTypes
    for ft in root.findall("fieldType"):
        analyzers = []
        for analyzer_elem in ft.findall("analyzer"):
            tokenizer = analyzer_elem.find("tokenizer")
            filters = analyzer_elem.findall("filter")
            analyzers.append({
                "type": analyzer_elem.get("type"),
                "tokenizer": {"class": tokenizer.get("class")} if tokenizer is not None else None,
                "filters": [{k: v for k, v in f.items()} for f in filters]
            })
        field_types.append({
            "name": ft.get("name"),
            "class": ft.get("class"),
            "positionIncrementGap": ft.get("positionIncrementGap", "100"),
            "analyzers": analyzers
        })

    # Parse fields
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

def main():
    for entry in cores:
        schema_file = entry["schema"]
        solr_url = entry["url"]
        print(f"Processing core '{entry['core']}' with schema '{schema_file}'...")
        field_types, fields = parse_schema(schema_file)
        add_to_solr(solr_url, field_types, fields)
        print(f"✅ Schema uploaded for core '{entry['core']}'\n")

if __name__ == "__main__":
    # not tested yet
    main()
    