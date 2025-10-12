import os
import pandas as pd
from lastfmapi_utils import augment_csv_with_lastfm

process_dir = r"c:\FEUP\MEIC\PRI\processData"
os.makedirs(process_dir, exist_ok=True)

csv_path = r"c:\FEUP\MEIC\PRI\dataset\spotify_millsongdata.csv"
out_csv_path = os.path.join(process_dir, "spotify_millsongdata_with_lastfm.csv")
progress_file = os.path.join(process_dir, "lastfm_progress.json")

augment_csv_with_lastfm(
    csv_path,
    out_csv_path=out_csv_path,
    overwrite=False,         
    chunk_size=200,         
    progress_file=progress_file,
    sleep_between_calls=0.2  
)

print("Processamento completo!")
print("Songs file:", out_csv_path)
print("Artists file:", out_csv_path.replace('.csv', '_artists.csv'))