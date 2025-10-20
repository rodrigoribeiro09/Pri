#!/bin/bash

# This script expects a container started with the following command.
# docker run -p 8983:8983 --name song_solr -v ${PWD}/dataset:/data -d solr:9 solr-precreate dataset

# Schema definition via API
docker exec -it song_solr sh -c 'bin/solr post -c dataset /data/dataset.csv'

# Populate collection using mapped path inside container.
