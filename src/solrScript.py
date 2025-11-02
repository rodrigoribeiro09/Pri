import requests
import xml.etree.ElementTree as ET

SOLR_URL = "http://localhost:8983/solr/songs/schema"
SCHEMA_FILE = "solr/schema.xml"  


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


def main():
    field_types, fields = parse_schema(SCHEMA_FILE)
    add_to_solr(field_types, fields)
    print("✅ Schema upload completed!")


if __name__ == "__main__":
    main()
