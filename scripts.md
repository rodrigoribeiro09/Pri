- docker run -d --name song_solr -p 8983:8983 -v ${PWD}/dataset:/data solr:9

## Create core:
- docker exec -it song_solr  bin/solr create_core -c songs 
## Add schema:
- doubt, whem im adding the schema is delting the old default solr schema which dont make any sense
- DO i need to updtate the schema phrase by phase using the api?
-  docker cp solr/schema.xml song_solr:/var/solr/data/songs/conf/managed-schema
- Run python script
## Adicionar os docs:
docker exec -it song_solr sh -c 'bin/solr post -c songs /data/dataset.csv'
## Add Stop-words
- No need 
docker cp solr/stopwords.txt song_solr:/var/solr/data/songs/conf/stopwords.txt


### Duvidas:
- os filtros estao a ser chamados mas nao aplicados
- stop words not working-working
- psf working

