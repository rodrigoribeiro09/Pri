import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_data():

    csv_songs = pd.read_csv('../dataset/spotify_millsongdata.csv')
    print("data loaded")

    return csv_songs


import pandas as pd

import pandas as pd


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
