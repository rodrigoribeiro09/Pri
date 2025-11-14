import string
import nltk
from nltk.corpus import wordnet, stopwords
import pandas as pd
import string
from nltk.tokenize import word_tokenize
import json
import os


def get_wordnet_synonyms(word):

    """
    Consulta o WordNet para encontrar sinónimos de uma palavra.
    """
    synonyms = set()
    word_lower = word.lower()
    
    for syn in wordnet.synsets(word_lower):
        for lemma in syn.lemmas():
            synonym_candidate = lemma.name().replace('_', ' ').lower()
            synonyms.add(synonym_candidate)
    
    synonyms.discard(word_lower)
    return list(synonyms)

def generate_synonyms_from_txt(input_filename, output_filename):
    try:
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('punkt')
        stop_words = set(stopwords.words('english'))
        translator = str.maketrans('', '', string.punctuation)

        with open(input_filename, "r", encoding="utf-8") as f:
            raw_words = f.readlines()

        words_to_process = set()
        for word in raw_words:
            word = word.strip().lower()
            word = word.translate(translator)
            if word and word not in stop_words and word.isalpha():
                words_to_process.add(word)

        print(f"Foram encontradas {len(words_to_process)} palavras únicas para processar.")

        unique_words_list = sorted(list(words_to_process))
        total_words = len(unique_words_list)

        with open(output_filename, "w", encoding="utf-8") as f:
            for i, word in enumerate(unique_words_list):
                print(f"Progresso: {i+1}/{total_words} | Mapeando: '{word}'")
                syns = get_wordnet_synonyms(word)
                if syns:
                    # Junta com vírgulas e sem vírgula no final
                    line = word + "," + ",".join(syns)
                    f.write(line + "\n")

        print(f"✅ Dicionário de sinónimos guardado em '{output_filename}'")

    except FileNotFoundError:
        print(f"ERRO: Não foi possível encontrar o ficheiro '{input_filename}'")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# -------------------------------------------------------------



def get_synonyms(word, pos_tags=[wordnet.NOUN, wordnet.VERB]):
    synonyms = set()
    word_lower = word.lower()
    for pos in pos_tags:
        for syn in wordnet.synsets(word_lower, pos=pos):
            for lemma in syn.lemmas():
                synonym_candidate = lemma.name().replace("_", " ").lower()
                if synonym_candidate != word_lower:
                    synonyms.add(synonym_candidate)
    return list(synonyms)

def generate_wordnet_synonyms(input_csv, output_file, columns=None, pos_tags=[wordnet.NOUN, wordnet.VERB]):
    if columns is None:
        columns = ['song_name', 'album_name', 'song_lyrics', 'artist_bio']

    # Check file exists
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"{input_csv} not found!")

    # Download NLTK resources
    nltk_data_path = os.path.expanduser('~/nltk_data')
    nltk.data.path.append(nltk_data_path)

    # Baixar recursos necessários
    nltk.download('punkt', download_dir=nltk_data_path, quiet=True)   # tokenizador
    nltk.download('punkt_tab', download_dir=nltk_data_path, quiet=True)  # evita erro punkt_tab
    nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
    nltk.download('omw-1.4', download_dir=nltk_data_path, quiet=True)
    nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)
    stop_words = set(stopwords.words('english'))
    translator = str.maketrans('', '', string.punctuation)
    print("✅ NLTK resources downloaded.")
    df = pd.read_csv(input_csv)
    all_words = set()

    for col in columns:
        if col not in df.columns:
            continue
        for text in df[col]:
            tokens = word_tokenize(str(text))
            for word in tokens:
                cleaned_word = word.lower().translate(translator)
                if cleaned_word.isalpha() and cleaned_word not in stop_words:
                    all_words.add(cleaned_word)
                    print(f"Collected word: {cleaned_word}")

    synonyms_mapping = {}
    for word in sorted(all_words):
        syns = get_synonyms(word, pos_tags)
        print(f"Word: '{word}' | Synonyms found: {len(syns)}")
        if syns:
            synonyms_mapping[word] = syns

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(synonyms_mapping, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved {len(synonyms_mapping)} words with synonyms to '{output_file}'")




def json_to_txt(json_file_path, output_file_path):
   
    # Open and load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Write to TXT file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for key, values in data.items():
            line = ', '.join([key] + values)
            f.write(line + '\n')


if __name__ == "__main__":
    input_filename = "solr/words_list.txt"  
    output_filename = "solr/synonyms_output_raw.txt"
    generate_synonyms_from_txt(input_filename, output_filename)
    