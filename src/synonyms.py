import pandas as pd
import string
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet # <--- NOVO IMPORT

input_filename = "../dataset/dataset.csv"
output_filename = "synonyms_output_wordnet.txt" # Mudei o nome do ficheiro de saída para evitar sobrescrever

# -------------------------------------------------------------
## 2. Função de Consulta ao WordNet
def get_wordnet_synonyms(word):
    """
    Consulta o WordNet para encontrar sinónimos de uma palavra localmente.
    """
    synonyms = set()
    word_lower = word.lower()
    
    # Itera sobre todos os 'synsets' (conjuntos de sinónimos) para a palavra
    for syn in wordnet.synsets(word_lower):
        # Itera sobre os 'lemmas' (formas da palavra) dentro de cada synset
        for lemma in syn.lemmas():
            # Adiciona o sinónimo, substituindo sublinhados por espaços e convertendo para minúsculas
            synonym_candidate = lemma.name().replace('_', ' ').lower()
            synonyms.add(synonym_candidate)
            
    # O WordNet pode incluir a própria palavra como sinónimo, removemos
    synonyms.discard(word_lower) 
    
    return list(synonyms)

# -------------------------------------------------------------
try:
    # Download dos recursos NLTK (permanece igual)
    print("A descarregar recursos NLTK (necessário apenas na primeira vez)...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

    # Preparar ferramentas de limpeza de texto (permanece igual)
    stop_words = set(stopwords.words('english'))
    translator = str.maketrans('', '', string.punctuation)

    # Ler o dataset (permanece igual)
    df = pd.read_csv(input_filename)
    
    print(f"Dataset '{input_filename}' lido com sucesso.")

    all_words = set()
    
    # 🌟 NOVA CONFIGURAÇÃO: Definir as colunas a processar
    columns_to_process = ['song_lyrics', 'artist_bio']
    
    # Iterar sobre as colunas
    print(f"A processar palavras únicas nas colunas: {columns_to_process}...")
    
    for column_name in columns_to_process:
        print(f"-> A processar coluna '{column_name}'...")
        
        # Itera sobre o texto em cada linha da coluna
        for text_content in df[column_name]:
            # Certifica-se de que o conteúdo é tratado como string
            tokens = word_tokenize(str(text_content))
            
            for word in tokens:
                # 2. Converter para minúsculas
                lowered_word = word.lower()
                
                # 3. Remover pontuação
                cleaned_word = lowered_word.translate(translator)
                
                # 4. Verificar se é uma palavra válida
                if (cleaned_word not in stop_words and
                    cleaned_word != '' and
                    cleaned_word.isalpha()):
                    
                    all_words.add(cleaned_word)


    print(f"Foram encontradas {len(all_words)} palavras únicas nas letras e biografias.")

# -------------------------------------------------------------
## 4. Consultar o WordNet e Criar o Dicionário de Mapeamento (MODIFICADO)
    
    # Inicializa o dicionário de saída
    synonyms_mapping = {}
    unique_words_list = sorted(list(all_words)) # Ordena para garantir um processamento consistente
    total_words = len(unique_words_list)

    print(f"\nA iniciar consulta LOCAL e mapeamento para {total_words} palavras...")
    
    for i, word in enumerate(unique_words_list):
        # Mostrar progresso
        print(f"Progresso: {i+1}/{total_words} | Mapeando: '{word}'")
        
        syns = get_wordnet_synonyms(word) 
        
        # Só adiciona a palavra ao dicionário se encontrar sinónimos
        if syns:
            synonyms_mapping[word] = syns 

    print(f"\nMapeamento WordNet terminado. Foram mapeadas {len(synonyms_mapping)} palavras com sinónimos.")

# -------------------------------------------------------------
## 5. Guardar o Dicionário de Mapeamento em JSON (MODIFICADO)
    
    with open(output_filename, "w", encoding="utf-8") as f:
        # Usa json.dump para escrever o dicionário no ficheiro
        # indent=4 torna o ficheiro legível
        json.dump(synonyms_mapping, f, indent=4, ensure_ascii=False)
            
    print(f"SUCESSO: Dicionário de sinónimos guardado em '{output_filename}'")

except FileNotFoundError:
    print(f"ERRO: Não foi possível encontrar o ficheiro '{input_filename}'")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")