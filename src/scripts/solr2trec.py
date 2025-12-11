#!/usr/bin/env python3

import argparse
import json
import sys

def solr_to_trec(solr_response, run_id="run0"):
    for query_id, response in solr_response.items():
        try:
            docs = response["response"]["docs"]
            for rank, doc in enumerate(docs, start=1):
                print(f"{int(query_id)} Q0 {doc['id']} {rank} {doc['score']} {run_id}")
        except KeyError:
            print("Error: Invalid Solr response format. 'docs' key not found.")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Solr results to TREC format.")
    parser.add_argument("--run-id", type=str, default="run0", help="Experiment or system identifier (default: run0).")
    parser.add_argument("--input", type=str, help="Path to JSON file with Solr results. If not provided, reads from stdin.")

    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            solr_response = json.load(f)
    else:
        solr_response = json.load(sys.stdin)

    solr_to_trec(solr_response, args.run_id)
