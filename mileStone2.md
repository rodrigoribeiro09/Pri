# Solar
## Schema

- **song_id**
  - `string` → exact match (IDs should not be tokenized)
  - `indexed="true"` → can search by song ID
  - `stored="true"` → value returned in search results
  - `uniqueKey` → ensures each document has a unique identifier

- **song_name**
  - `text_general` → allows full-text search (case-insensitive, tokenized)
  - `indexed="true"` → searchable
  - `stored="true"` → returned in results
  - Useful for searching by partial titles or keywords

- **song_lyrics**
  - `text_general` → full-text searchable lyrics
  - `indexed="true"` → searchable
  - `stored="true"` → returned in results
  - Enables searching for words or phrases inside the lyrics

- **album_name**
  - `string` → exact value, not tokenized
  - `indexed="true"` → searchable for exact matches
  - `stored="true"` → returned in results
  - Useful for faceting, filtering, or sorting albums

- **artist_name**
  - `string` → exact value, not tokenized
  - `indexed="true"` → searchable by exact match
  - `stored="true"` → returned in results
  - Efficient for repeated values like artist names

- **artist_bio**
  - `text_general` → full-text searchable biography
  - `indexed="true"` → searchable
  - `stored="true"` → returned in results
  - Enables searching for keywords or phrases in the artist’s bio
