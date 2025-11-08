## Create container:
docker run -d --name song_solr -p 8983:8983 -v ${PWD}/dataset:/data solr:9
## Create core:
docker exec -it song_solr  bin/solr create_core -c songs 
## Add schema:
python .\src\solrScript.py
## Adicionar os docs:
docker exec -it song_solr sh -c 'bin/solr post -c songs /data/dataset.csv'



