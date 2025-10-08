import pandas as pd
from lastfmapi_utils import augment_csv_with_lastfm

# Caminho para o teu CSV original
csv_path = r"c:\FEUP\MEIC\PRI\dataset\spotify_millsongdata.csv"
out_csv_path = r"c:\FEUP\MEIC\PRI\dataset\spotify_millsongdata_with_lastfm.csv"

augment_csv_with_lastfm(
    csv_path,
    out_csv_path=out_csv_path,
    overwrite=False,         # apaga o ficheiro de saída se já existir
    chunk_size=200,         # ajusta conforme a RAM disponível
    sleep_between_calls=0.2 # para evitar rate-limit
)

print("Processamento completo! Vê o ficheiro:", out_csv_path)