import pandas as pd

artists = pd.read_csv('./finalDataset/artist.csv')
songs = pd.read_csv('./finalDataset/song.csv')

merged_df = pd.merge(songs, artists, how='left', left_on='artist_id', right_on='artist_id')

final_df = merged_df[['song_id', 'song_name', 'song_lyrics', 'album_name', 'artist_name', 'artist_bio']]

final_df.to_csv('./finalDataset/dataset.csv', index=False)