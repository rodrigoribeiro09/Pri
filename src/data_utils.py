import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_data():

    csv_songs = pd.read_csv('../dataset/spotify_millsongdata.csv')
    print("data loaded")

    return csv_songs


def load_process_data():
    csv_songs = pd.read_csv('processData/song.csv')
    csv_artist = pd.read_csv('processData/artist.csv')
    print("data loaded")

    return csv_songs, csv_artist



def averaNSongPerArtist(df):
    songs_per_artist = df.groupby('artist')['song'].count()
    average_songs = songs_per_artist.mean()
    return average_songs


def dataAnalysis(df):
    """
    Perform basic exploratory data analysis on a DataFrame.
    Prints dataset overview, missing values, duplicates, basic stats, and sample distributions.
    """
    
    print("===== DATAFRAME SHAPE =====")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}\n")
    
    print("===== COLUMN NAMES AND DATA TYPES =====")
    print(df.dtypes, "\n")
    

    print("===== MISSING VALUES =====")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values\n")
    
    print("===== DUPLICATE ROWS =====")
    dup_rows = df[df.duplicated()]
    print(f"Number of duplicate rows: {dup_rows.shape[0]}\n")
    
    
    print("===== UNIQUE VALUES PER COLUMN =====")
    for col in df.columns:
        print(f"{col}: {df[col].nunique()} unique values")
    print()
    print("===== Average song per artis =====")
    print(averaNSongPerArtist(df))
    print()
    print("===== BASIC STATISTICS FOR NUMERIC COLUMNS =====")
    numeric_cols = df.select_dtypes(include='number')
    if not numeric_cols.empty:
        print(numeric_cols.describe(), "\n")
    else:
        print("No numeric columns.\n")
    
    print("===== MOST FREQUENT VALUES FOR CATEGORICAL COLUMNS =====")
    cat_cols = df.select_dtypes(include='object')
    for col in cat_cols:
        top = df[col].value_counts().head(5)
        print(f"{col}:\n{top}\n")
    
def plot_artist_frequency(df, col='artist', top_n=20,most=True):
    """
    Plots the frequency of artists in the dataset as a bar chart.

    Parameters:
        df (pd.DataFrame): The dataset.
        col (str): Column name containing artist names.
        top_n (int): Number of top artists to display.
        most(bool):if true the top_n if false the least_n
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in the DataFrame.")

    # Count occurrences of each artist
    if(most):
        artist_counts = df[col].value_counts().head(top_n)
    else:
        artist_counts = df[col].value_counts().tail(top_n)

    # Plot
    plt.figure(figsize=(12,6))
    artist_counts.plot(kind='bar', color='skyblue')
    plt.title(f"Top {top_n} Most Frequent Artists") if most else plt.title(f"Top {top_n} Least Frequent Artists")
    plt.xlabel("Artist")
    plt.ylabel("Number of Songs")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()




def plot_column_frequency(df, col, top_n=20):
    """
    Plots the frequency of values in a specified column.
    
    Parameters:
        df (pd.DataFrame): Dataset to analyze.
        col (str): Column name to check frequency.
        top_n (int): Number of top values to display.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in the DataFrame.")
    
    # Contar frequência de cada valor
    counts = df[col].value_counts().head(top_n)
    
    # Plot
    plt.figure(figsize=(12,6))
    counts.plot(kind='bar', color='skyblue')
    plt.title(f"Top {top_n} Most Frequent Values in '{col}'")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()



def dataProcessAnalysis(df):
    """
    Perform basic exploratory data analysis on a DataFrame.
    Prints dataset overview, missing values, duplicates, basic stats, and sample distributions.
    """
    
    print("===== DATAFRAME SHAPE =====")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}\n")
    
    print("===== COLUMN NAMES AND DATA TYPES =====")
    print(df.dtypes, "\n")
    

    print("===== MISSING VALUES =====")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values\n")
    
    print("===== DUPLICATE ROWS =====")
    dup_rows = df[df.duplicated()]
    print(f"Number of duplicate rows: {dup_rows.shape[0]}\n")
    
    
    print("===== UNIQUE VALUES PER COLUMN =====")
    for col in df.columns:
        print(f"{col}: {df[col].nunique()} unique values")
    print()

    

    
def getWrongArtistBios(df):
    # Filter conditions
    multiple_artistsId = df.loc[df['lastfm_artist_bio'].str.startswith("There are", na=False), 'id'].tolist()

# IDs where artist_bio is exactly "Read more on Last.fm"
    read_moreId = df.loc[df['lastfm_artist_bio'].str.strip().eq("Read more on Last.fm"), 'id'].tolist()


    # Count occurrences
    counts = {
        "Starts with 'There are'": len(multiple_artistsId),
        "Read more on Last.fm": len(read_moreId)
    }

    # Show plot
    plt.bar(counts.keys(), counts.values())
    plt.title("Contagem de artist_bio problemáticos")
    plt.ylabel("Número de ocorrências")
    plt.xticks(rotation=15)
    plt.show()

    return  multiple_artistsId+read_moreId


def getWrongMusic(df, wrong_ids):
    # Filter rows where artist_id is in wrong_ids
    wrong_music = df[df['artist_id'].isin(wrong_ids)]
    
    # Return only the song titles as a list
    d= wrong_music['song'].tolist()

    print("number of music that have wrong artist bio:")
    print(len(d))
    print("Music names")
    print(d)
    return d


def addIdToArtist(artistcsv):
    df_artsit=  pd.read_csv(artistcsv)
    if 'id' not in df_artsit.columns:
        df_artsit.insert(0, 'id', range(1, len(df_artsit) + 1))
        df_artsit.to_csv(artistcsv, index=False)
        print(f"'id' column added to {artistcsv}.")

def remove_lastfm_artist_name(artistcsv):
    df_artsit=  pd.read_csv(artistcsv)
    if 'lastfm_artist_name' in df_artsit.columns:
        df_artsit.drop(columns=['lastfm_artist_name'], inplace=True)
        df_artsit.to_csv(artistcsv, index=False)
        print(f"'lastfm_artist_name' column removed from {artistcsv}.")
    
def connectArtistSong(artistcsv, songcsv):
    df_artist = pd.read_csv(artistcsv)
    df_song = pd.read_csv(songcsv)

    merged_df = pd.merge(
        df_song,
        df_artist[['id', 'artist']],
        on='artist', 
        how='left'
    )

    merged_df.drop(columns=['artist'], inplace=True)
    merged_df.rename(columns={'id': 'artist_id'}, inplace=True)

    return merged_df

def removeLinkToSong(df):
    if 'link' in df.columns:
        df.drop(columns=['link'], inplace=True)
        print("'link' column removed from DataFrame.")
    else:
        print("No 'link' column found.")

def count_short_values(df: pd.DataFrame, column: str) -> int:
  
    return df[column].astype(str).apply(len).lt(4).sum()


def plot_short_string_values(df: pd.DataFrame, column: str, min_len: int = 4):
    """
    Mostra um gráfico de barras com a frequência de strings 
    com comprimento menor que 'min_len' numa dada coluna.

    Args:
        df (pd.DataFrame): DataFrame a analisar.
        column (str): Nome da coluna.
        min_len (int): Comprimento máximo para considerar 'curto'. Default = 4.
    """
    # Seleciona apenas strings curtas
    short_values = df[column].dropna().astype(str)
    short_values = short_values[short_values.str.len() < min_len]

    if short_values.empty:
        print(f"Nenhum valor com len < {min_len} na coluna '{column}'.")
        return

    # Conta a frequência de cada valor curto
    value_counts = short_values.value_counts()

    # Cria o gráfico
    plt.figure(figsize=(6, 4))
    value_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f"Valores com len < {min_len} na coluna '{column}'")
    plt.xlabel("Valor")
    plt.ylabel("Frequência")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_top_frequent_strings(df, column: str, top_n: int = 10):
  
    
    value_counts = df[column].dropna().astype(str).value_counts().head(top_n)

    if value_counts.empty:
        print(f"Nenhum valor válido encontrado na coluna '{column}'.")
        return

    # Cria o gráfico
    plt.figure(figsize=(8, 5))
    value_counts.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title(f"Top {top_n} strings mais frequentes em '{column}'")
    plt.xlabel("Valor")
    plt.ylabel("Frequência")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


