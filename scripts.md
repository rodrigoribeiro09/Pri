## Create container:
docker run -d --name song_solr -p 8983:8983 -v ${PWD}/dataset:/data solr:9
## Create core:
docker exec -it song_solr  bin/solr create_core -c <CORENAME>
## Add schema:
python .\src\solrScript.py
## Adicionar os docs:
docker exec -it song_solr sh -c 'bin/solr post -c <CORENAME> /data/dataset.csv'
## Add synonyms
docker cp solr/synonyms.txt song_solr:/var/solr/data/<CORENAME>/conf/
docker cp solr/stopwords.txt song_solr:/var/solr/data/<CORENAME>/conf/


## Delete core
curl "http://localhost:8983/solr/admin/cores?action=UNLOAD&core=songs_test&deleteInstanceDir=true" 

# Eval pipeline
## Correr queries:
python3 scripts/query_solr.py --queries config/queries --uri http://localhost:8983/solr --collection songs
## resultados para terc:
python3 scripts/solr2trec.py --run-id run1 --input results/solr_output.json > results/trec_run.txt
## Transformar os qrels em terec:
python3 scripts/qrels2trec.py --qrels config/qrels > results/qrels.trec
## Avalie com trec_eval
- Need to be inside the trec:eval
- If you dont have the trec_eval run makefile
- trec_eval -q -m all_trec results/qrels.trec results/trec_run.txt | scripts/plot_pr.py

