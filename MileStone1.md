#  Data Preparation
## Idea:
- The main idea of this project is to develop an information retrieval system for a music dataset, where users can search for songs and explore relationships with their artists and other important attributes.
- In this context, the main unstructured attributes are the song lyrics and the artist descriptions.
- Our approach is to find a rich music dataset that contains a large collection of songs from different artists, with the lyrics included as an attribute, and then combine it with another dataset that provides detailed artist descriptions.
- Alternatively, we plan to retrieve the artist descriptions from the Wikipedia API to enrich the dataset.
## search repositories for datasets

| Dataset URL | Attributes | Pros | Cons | Database Type |
|-------------|------------|------|------|---------------|
| [Audio features and lyrics of Spotify songs](https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs/data) | track_id, track_name, track_artist, lyrics, track_popularity, track_album_id, track_album_name, track_album_release_date, playlist_name, playlist_id, playlist_genre, playlist_subgenre, danceability, energy, key, loudness, mode, speechiness, instrumentalness, liveness, valence, tempo, duration_ms, language | A lot of information about the songs and many different tracks | Some songs don’t have lyrics and the number of songs per artist is a bit limited. Too many non-essential attributes | Songs |
| [Spotify Million Song Dataset](https://www.kaggle.com/datasets/notshrirang/spotify-million-song-dataset) | song_name, artist_name, link, lyrics | Good balance of attributes, consistent number of songs per artist, and overall a well-sized dataset | Some inconsistencies in how values are obtained — description states data comes from the Spotify API, but song links are from a lyrics website | Songs |
| [Lyrics and Metadata from 1950 to 2019](https://data.mendeley.com/datasets/3t9vbwxgr5/2) | artist_name, track_name, release_date, genre, lyrics, len, dating, violence, world/life, night/time, shake the audience, family/gospel, romantic, communication, obscene, music, movement/places, light/visual perceptions, family/spiritual, like/girls, sadness, feelings, danceability, loudness, acousticness, instrumentalness, valence, energy, topic, age | Very rich dataset with a large number of songs and detailed metadata | May have too many artists with only a few songs each and includes many non-essential attributes | Songs |
| [Artists](https://www.upf.edu/web/mtg/semantic-similarity) | artist_name,artist_mbid,biography,top_10_similar_mbids,dbpedia_uri | Very rich dataset with a large number of artists and detailed metadata | Its not a raw dataSet, its a set of files that need to be conected can be harder to work  | Artists |


## Web scraping / crawling
- Maybe this is the best aprouch since there is not a lot of good datasbases with the artist bio

| Option Name | Method | Pros | Cons |
|-------------|--------|------|------|
| Wikipedia | Web scraping of artist pages | Usually rich and up-to-date textual content; covers a wide range of artists; freely accessible | Needs to handle disambiguation of artist names; scraping may be blocked if too many requests; text may require cleaning |
| DBpedia | SPARQL queries on DBpedia endpoint | Structured data extracted from Wikipedia; supports multiple languages; can get abstracts directly | Limited to artists with DBpedia entries; not all biographies are complete; requires knowledge of SPARQL |
| Wikidata | SPARQL queries on Wikidata endpoint | Very structured; easy to link with other datasets via QIDs; can extract multiple attributes | Not all artists have detailed biographies; abstracts are shorter than Wikipedia; requires SPARQL knowledge |
| Last.fm API | Queries the `artist.getInfo` endpoint to get `bio.content` | Easy to use; provides textual content ready for NLP | Low rate limiting (but manageable if calls are distributed) |
| Genius API | Queries the `/search` endpoint and retrieves the artist page `/artists/:id` | Focused on artist bios; very rich content | Low rate limiting; requires an API key |
