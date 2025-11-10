import json

json_filename = "synonyms_output_wordnet.json"
output_filename = "synonyms.txt"

try:
    # --- 1. CARREGAR JSON ---
    with open(json_filename, 'r', encoding='utf-8') as f:
        synonyms_mapping = json.load(f)
        
    print(f"Sucesso: O dicionário foi carregado a partir de '{json_filename}'.")
    print(f"Número de palavras mapeadas: {len(synonyms_mapping)}")

    # --- 2. CONVERTER E FORMATAR ---
    output_lines = []
    
    for word, synonyms in synonyms_mapping.items():
        # Lógica de formatação (perfeita para o Solr/WordNet)
        line_parts = [word] + synonyms
        line = ", ".join(line_parts) 
        output_lines.append(line)

    # --- 3. GUARDAR TXT ---
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"Sucesso: O ficheiro '{output_filename}' foi criado no formato Solr/WordNet.")

except FileNotFoundError:
    print(f"ERRO: O ficheiro '{json_filename}' não foi encontrado. Verifique se está na pasta correta.")
except json.JSONDecodeError:
    print(f"ERRO: O ficheiro '{json_filename}' está corrompido ou mal formatado em JSON.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")