# PRI


## MIle 3
- Adicionar os embeeding as lyrics das musicas
- Adicionar o vector dense ao schema do solr

- Mantém a criação dos 3 cores (simple, songs, boosted) com bin/solr create_core e a cópia de synonyms_hand.txt e stopwords.txt para cada conf.​

- Para o core boosted, chama configure_vector_field, que usa a Schema API para:

    - criar o fieldType songVector como solr.DenseVectorField com vectorDimension=384, similarityFunction=cosine e knnAlgorithm=hnsw, alinhado com a doc de DenseVectorField;​
    - criar o campo vector deste tipo, indexed e stored, para guardar os embeddings no índice e permitir queries knn.​
    - Hybrid search:
        - Os resultados é intreceção do semantic search com o lexical search:
        - Refrencias-https://sease.io/2023/12/hybrid-search-with-apache-solr.html
        - Vetorial (KNN) encontra os topK resultados semanticamente relevantes.
        - Lexical (eDisMax) é executado apenas dentro desse conjunto, e o score textual define a ordenação final que o utilizador vê.

# Melhorias mile 2
- Adicionar synonim flatten no squema-
- Data cleaning :
    - remoção de alguns artistas que tinham a biografia incopleta. Foi feito uma filtragem com artistas que tinham biografia com as keywors"wrong tag, pls chcck your tags"

## Adicionar ao datast sources:
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

## ADICIONAR a semantic searhc(nova secção):
- Semantic searhc:
    - No dataset deste sistema foi adicinado um campo com os embeedings das lyrics das musicas obtidos atraves do modelo sentence-transformers/all-mpnet-base-v2
    - Para que o core deste sistema suporte pesquisa vetorial foi adicionado ao schema um campo do tipo solr.DenseVectorField.
    - Na fase de pesquisa, utilizamos o parser {!knn} do Solr, aplicando o algoritmo de KNN sobre o campo vector, que contém os embeddings das letras das músicas. O parâmetro topK=10 indica que serão recuperados os 10 documentos semanticamente mais próximos do vetor da query, com base numa métrica de similaridade.

## Adicionar a pipeline:

    - Semantic core:
        - sitema que apenas aplica pesquisa semantica atraves dos embeddings das lyrics das musicas
    - Sistema hibridos:
        - Ao schema deste sistema foi adicionado o campo vector do tipo solr.DenseVectorField para suportar pesquisa vetorial e Para alem disso foi adiciondo 2 novos atrituos ao dtaset artist_national e music_genres 

## Motivações das movas implementações(nova secção)
- Com os dados obtidos no m2 um dos nosso maiores problemas era alguns problemas de ambiguidade semanica por exemplo confusao entre love romantico e love como tema musical.Com isto um dos principais improvemnte para resolver isto foi adicionar um search semantico atraves dos embeddings das lyrics das musicas.Apenas escolhemps as lyrics porque era a feature textual mais relevante para o conteudo das musicas, podiamos tambem aplicado no bio dos artistas mas talvez nao teriamos tanto relevancia pois este feature apenas e um complemento ao conteudo das musicas.
- Outro grande problema que tinhamos principamente nas In sobre a nacionalidade dos artistas e os generos musicais era identifcação destes atributos apatir da biografia do artistas em que em muitos casos as biograficas eram incompletas e nao continham essa informacao, oque tornava dificil a sua indexaçao e consequente pesquisa.Para resolver isto adicionamos estas novas fontes de dados que nos permitiram enriquecer o dataset com estes atributos adicimos artist_nationality e music_genres dando um grande boost a estes 2 atriubtos pois acabam por ser  bastatne unicos pois se nas keywords da query encontram um hit com um documento este documento tem de ser bastante relevante para o utilizador, isto porque os atributos em questao nao tem grande variablidae e sao bastante especificos.

## Explicaçãp do sistem final de m3. 
- O nosos sistema final e um sistema hibrido que combina pesquisa lexical e semantica.

- semantica seach;
    - Inicialmente temos uma pesquisa semantica que procura os TopK documentos mais relevantes para a query atraves dos embeddings das lyrics das musicas o valor topK é igual ao numero de rows*10 (rows e o nuemro de resultados) usamos este valor para garantir que temos resultados suficientes para a pesquisa lexical e para aumentar o recall. 

- Lexical search:
    - Depois aplicamos uma pesquisaca lexical atraves do edismax com os atributos song_lyrics,song_name,artist_name,artist_bio,album_name,artist_nationality esong_genre
    - Query config:
        - Género e nacionalidade:
            - artist_nationality^15 e song_genre^15 em qf: tratam género e nacionalidade como filtros muito específicos; se a query menciona “rock”, “american”, etc., esses campos passam a ser determinantes.
            - pf1 com artist_nationality^12 e song_genre^12: quando um único termo crítico (género/país) aparece nesses campos, o doc recebe um boost ainda mais forte, ideal para queries curtas tipo “american rock”.
        - Letras:
            - song_lyrics^4 em qf: dá peso alto à letra como principal sinal semântico da música.
            - song_lyrics^3 em pf/pf2: reforça quando os termos da query aparecem juntos ou próximos na letra, o que beneficia queries descritivas ou com frases.
        - Artista, bio, álbum, título:
            - artist_name^2 e song_name^2 em qf: ajudam a resolver queries de identificação (“bohemian rhapsody queen”), mas com peso controlado para não dominarem queries temáticas.

            - artist_bio^2 em qf + artist_bio^2 em pf/pf2 e artist_bio^3 em pf1: a bio funciona como contexto biográfico/discográfico que reforça queries com pistas sobre a carreira, sem ultrapassar lyrics/género/nacionalidade.
            - album_name^1 em qf: contribui ligeiramente quando a query menciona nomes de álbuns, funcionando mais como desempate do que como fator principal.
- Hibrid search:
    - O sitema hibrido combina os resultados da pesquisa semântica e lexical:
        - A pesquisa semântica retorna os TopK documentos mais relevantes com base nos embeddings.
        - A pesquisa lexical é então aplicada apenas a esse conjunto, e o score textual determina a ordenação final.
        - Refrencias-https://sease.io/2023/12/hybrid-search-with-apache-solr.html
