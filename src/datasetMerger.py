import pandas as pd

# Load the data
artists = pd.read_csv('./finalDataset/artist.csv')
songs = pd.read_csv('./finalDataset/song.csv')

# Merge the DataFrames based on the artist_id (or whatever the common key is)
merged_df = pd.merge(songs, artists, how='left', left_on='artist_id', right_on='artist_id')

# Create the final DataFrame with the relevant columns
final_df = merged_df[['song_id', 'song_name', 'song_lyrics', 'album_name', 'artist_name', 'artist_bio']]

# Save to CSV
final_df.to_csv('./finalDataset/dataset.csv', index=False)