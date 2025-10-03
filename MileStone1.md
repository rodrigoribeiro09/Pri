


# 1º Milestone
## Abstract
Music information is an important area in modern information systems, with applications ranging from recommendation engines to lyric-based search platforms. In this project, we present <b>Tunix</b>, a text-based search system inspired by Shazam, but designed to work without audio input. Instead, <b>Tunix</b> allows users to search for songs by typing lyrics, retrieving corresponding tracks, artists, and descriptive metadata.

The final system aims to provide efficient lyric-based search functionality, offering accurate results along with artist descriptions and related attributes, thereby improving music discovery through text queries.

## Introduction
Music retrieval systems such as Shazam have transformed how users interact with music, but they are primarily based on audio fingerprinting. In many cases, users may remember a fragment of lyrics rather than the melody. This project addresses this gap by creating <b>Tunix</b>, a system that retrieves songs, artists, and related information based on text queries derived from lyrics.

<b>Tunix</b> will integrate datasets containing tracks, artists, lyrics, and metadata into a unified and searchable database. The system is designed to return not only the matching track but also relevant contextual information such as artist biography and related metadata. This project contributes to the field of Information Retrieval by developing a structured pipeline for music data collection and preparation, enabling efficient and accurate text-based search functionalities.

## Data Sources


| Dataset URL | Attributes | Pros | Cons | Database Type |
|-------------|------------|------|------|---------------|
| [Audio features and lyrics of Spotify songs](https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs/data) | track_id, track_name, track_artist, lyrics, track_popularity, track_album_id, track_album_name, track_album_release_date, playlist_name, playlist_id, playlist_genre, playlist_subgenre, danceability, energy, key, loudness, mode, speechiness, instrumentalness, liveness, valence, tempo, duration_ms, language | A lot of information about the songs and many different tracks | Some songs don’t have lyrics and the number of songs per artist is a bit limited. Too many non-essential attributes | Songs |
| [Spotify Million Song Dataset](https://www.kaggle.com/datasets/notshrirang/spotify-million-song-dataset) | song_name, artist_name, link, lyrics | Good balance of attributes, consistent number of songs per artist, and overall a well-sized dataset | Some inconsistencies in how values are obtained — description states data comes from the Spotify API, but song links are from a lyrics website | Songs |
| [Lyrics and Metadata from 1950 to 2019](https://data.mendeley.com/datasets/3t9vbwxgr5/2) | artist_name, track_name, release_date, genre, lyrics, len, dating, violence, world/life, night/time, shake the audience, family/gospel, romantic, communication, obscene, music, movement/places, light/visual perceptions, family/spiritual, like/girls, sadness, feelings, danceability, loudness, acousticness, instrumentalness, valence, energy, topic, age | Very rich dataset with a large number of songs and detailed metadata | May have too many artists with only a few songs each and includes many non-essential attributes | Songs |
| [Artists](https://www.upf.edu/web/mtg/semantic-similarity) | artist_name,artist_mbid,biography,top_10_similar_mbids,dbpedia_uri | Very rich dataset with a large number of artists and detailed metadata | Its not a raw dataSet, its a set of files that need to be conected can be harder to work  | Artists |


## Web Scraping / Crawling
Maybe this is the best aproach since there is not a lot of good datasbases with the artist bio

| Option Name | Method | Pros | Cons |
|-------------|--------|------|------|
| Wikipedia | Web scraping of artist pages | Usually rich and up-to-date textual content; covers a wide range of artists; freely accessible | Needs to handle disambiguation of artist names; scraping may be blocked if too many requests; text may require cleaning |
| DBpedia | SPARQL queries on DBpedia endpoint | Structured data extracted from Wikipedia; supports multiple languages; can get abstracts directly | Limited to artists with DBpedia entries; not all biographies are complete; requires knowledge of SPARQL |
| Wikidata | SPARQL queries on Wikidata endpoint | Very structured; easy to link with other datasets via QIDs; can extract multiple attributes | Not all artists have detailed biographies; abstracts are shorter than Wikipedia; requires SPARQL knowledge |
| Last.fm API | Queries the `artist.getInfo` endpoint to get `bio.content` | Easy to use; provides textual content ready for NLP | Low rate limiting (but manageable if calls are distributed) |
| Genius API | Queries the `/search` endpoint and retrieves the artist page `/artists/:id` | Focused on artist bios; very rich content | Low rate limiting; requires an API key |


## Data Processing Pipeline

The pipeline for data collection and preparation will be structured and reproducible, with the following stages:

1. **Data Acquisition**  
   - Download Kaggle and Mendeley datasets.  
   - Retrieve artist information using APIs (Last.fm, Genius, DBpedia).  

2. **Data Cleaning**  
   - Remove duplicates based on `track_id` and `(artist, song)` pairs.  
   - Normalize text (lowercasing, removing HTML tags, cleaning special characters).  
   - Handle missing values (drop or impute attributes as needed).  

3. **Data Integration**  
   - Join datasets on `track_name` and `artist_name`.  
   - Link artists with external biography sources via MBIDs or normalized names.  

4. **Storage**  
   - Store structured attributes (track metadata, artist info) in a relational database (PostgreSQL/SQLite).  
   - Store unstructured data (lyrics, biographies) in text collections for NLP tasks.  

5. **Reproducibility**  
   - Entire pipeline will be documented with Jupyter notebooks and scripts in Python (Pandas, Requests, BeautifulSoup, SQLAlchemy).  
   - Each step will be reproducible so that datasets can be re-fetched and re-processed if needed.

## Conceptual Data Model

Entities and relationships:

- **Artist** (artist_id, name, biography)  
  - Has → **Songs**  

- **Song** (song_id, title, lyrics, song_description)  
  - Belongs to → **Album**  
  - Performed by → **Artist**  

- **Album** (album_id, title, genre)  
  - Contains → **Songs**  

Relationships:  
- One Artist → Many Songs  
- One Album → Many Songs  
- One Song → One Artist, One Album  

## Final Collection Definition

The final collection will be a curated dataset consisting of:

- **Songs** with artists, album, lyrics and description 
- **Artists** with biographies and songs
- **Albums** with genre information 

All documents will be linked in a normalized schema. The collection will serve as the searchable index for the Tunix system.


## Follow-up Information Needs

The integrated dataset enables multiple information retrieval scenarios:

- **Lyric-based search**:  
  - Find songs containing given words/phrases.  
  - Search across multiple languages.  