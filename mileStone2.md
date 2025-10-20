# Solar
## Shema
- song_id: 
  - string → exact match (IDs should not be tokenized).
  - indexed="true" → can search by song ID.
  - stored="true" → value returned in search results.
  - required="true" → every document must have an I

- song_name:
    - text_general → allows full-text search (case-insensitive, tokenized).
    - indexed="true" → searchable.
    - stored="true" → returned in results.
- song_lyrics:
    - Lyrics are long text, in English.

    - text_en → uses English-specific analysis (stopwords, stemming).

    - Makes it easy to search for phrases or words inside lyrics.
- album_name & album_name_text:
    - album_name → exact value for faceting or sorting.

    - album_name_text → searchable text (partial matches).

    - copyField → copies album_name into album_name_text automatically for full-text search.

    - stored="false" → don’t store duplicate data.
  
- artist_name & artist_name_text:
    - album_name → exact value for faceting or sorting.

    - album_name_text → searchable text (partial matches).

    - copyField → copies album_name into album_name_text
    - automatically for full-text search.
    - stored="false" → don’t store duplicate data
- artist_bio:
    - text_en → English-specific text analysis.
    - Makes it easy to search for keywords in the artist’s bio.
    - stored="false" → don’t store duplicate data