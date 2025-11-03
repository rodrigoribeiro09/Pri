#!/bin/bash

# convert qrels to trec format
./scriptsTrec/qrels2trec.py --qrels config/qrels > qrels_trec.txt

# query solr and convert results to trec format
./scriptsTrec/query_solr.py \
    --queries config/queries \
    --collection courses | \
./scriptsTrec/solr2trec.py > results_trec.txt

# run evaluation pipeline
./trec_eval/trec_eval \
    -q -m all_trec \
    qrels_trec.txt results_trec.txt | ./scriptsTrec/plot_pr.py

# cleanup
rm qrels_trec.txt
rm results_trec.txt
