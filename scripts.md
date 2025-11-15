# Init :

## Create container:
docker run -d --name song_solr -p 8983:8983 -v ${PWD}/dataset:/data solr:9

- Antes de inicar os cores adicinem as key words que acham importants para o file solr/words_list (este deve estar vazio) e depois adicionem a mão ao ficheiro solr/synonyms_hand a mão pq o wordnet não é muito certo por isso double check 


# 1️⃣ Cria os cores e configura arquivos
python3 ./src/startSolr/init.py

# 2️⃣ Adiciona os schemas via Solr API
python3 ./src/startSolr/solrScript.py

# 3️⃣ Publica os documentos CSV nos cores
python3 ./src/startSolr/load_files_solr.py

----------------------------------------
# Eval pipeline

## Correr queries:
- difrentes queries do mesmo IN so difere o boost
- isto corre a 1 query no 1 schema a 2 no segundo e a 3 no 3, para cada query que queiram fazer criar 3 ficheiros seguidos para funcionar
- python3 .\scripts\query_solr.py
- python3 ./scripts/query_solr.py
## resultados para terc:

python3 scripts/solr2trec.py --run-id run1 --input results/solr_output.json > results/trec_run.txt
## Transformar os qrels em terec:
- aqui tem avaliar os results das voças queries a mão e adicionam os id relevantes ao qrel de cada query
- Depois:

python3 scripts/qrels2trec.py --qrels config/qrels > results/qrels.trec
## Avalie com trec_eval
- Run this in PRI not in trec_eval
- If you dont have the trec_eval run makefile
./trec_eval/trec_eval -q -m all_trec results/qrels.trec results/trec_run.txt \
    | python3 scripts/plot_pr.py



------------------------------------------------------

## Create core:
docker exec -it song_solr  bin/solr create_core -c <CORENAME>
## Add synonyms
docker cp solr/synonyms.txt song_solr:/var/solr/data/<CORENAME>/conf/
docker cp solr/stopwords.txt song_solr:/var/solr/data/<CORENAME>/conf/
## Add schema:
python .\src\solrScript.py
## Adicionar os docs:
docker exec -it song_solr sh -c 'bin/solr post -c <CORENAME> /data/dataset.csv'


## Delete core
curl "http://localhost:8983/solr/admin/cores?action=UNLOAD&core=songs_test&deleteInstanceDir=true" 


