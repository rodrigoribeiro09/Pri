# PRI

# Melhorias mile 2
- Adicionar synonim flatten no squema 
- Adicionar mais dados ao dastaser:
    - **Géneros musicais (Last.fm API)**:
        - Usar o last.fm API para obter géneros musicais associados a cada artista.
        - Caso apatir do nome da musica+artista nao exista uma tag do genero utilizar a tag do artista
        - Obtem :
            - genre_primary → género principal da música (ou do artista se não houver)
            - genre_all → lista de géneros secundários, separados por ;
    - **nacioonalidade dos artistas (musicbrainz)**:
        - Usar a MusicBrainz API para obter a nacionalidade de cada artista.
        - Obtem:
            - country → país de origem do artista (código ISO 3166-1 alpha-2)
            - area_name → nome da área ou país de origem do artista
- Data cleaning 

## MIle 3
- Adicionar os embeeding as lyrics das musicas
- Adicionar o vector dense ao schema do solr


- Mantém a criação dos 3 cores (simple, songs, boosted) com bin/solr create_core e a cópia de synonyms_hand.txt e stopwords.txt para cada conf.​

- Para o core boosted, chama configure_vector_field, que usa a Schema API para:

    - criar o fieldType songVector como solr.DenseVectorField com vectorDimension=384, similarityFunction=cosine e knnAlgorithm=hnsw, alinhado com a doc de DenseVectorField;​

    - criar o campo vector deste tipo, indexed e stored, para guardar os embeddings no índice e permitir queries knn.​
    - Q