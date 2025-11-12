# Solar

## analyze the documents and identify their indexable components:

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

## Tokenizers and Filters


In this Solr schema for English song lyrics and artist biographies, we use a combination of **tokenizers** and **filters** to process text for better search performance.

---

## Tokenizers

### StandardTokenizerFactory
- **Purpose:** Splits text into individual words (tokens) based on whitespace and punctuation.
- **Why:** Handles letters, numbers, and punctuation correctly, making it suitable for general English text such as lyrics and biographies.

---

## Filters

### LowerCaseFilterFactory
- **Purpose:** Converts all tokens to lowercase.
- **Why:** Ensures searches are **case-insensitive**, so words like `"Love"` and `"love"` are treated the same.

### StopFilterFactory
- **Purpose:** Removes common English stopwords.
- **Configuration:** Uses `ignoreCase="true"` and a stopwords file `stopwords.txt`.
- **Why:** Words like `"a"`, `"the"`, `"and"`, `"is"` are very frequent but usually do not add meaning to search queries. Removing them reduces noise and improves relevance.
- **Example:**

```
Input: "I am singing in the rain"
Output: "singing rain"
```

### SnowballPorterFilterFactory
- **Purpose:** Performs **stemming** on English words, reducing them to their root form.
- **Why:** Helps match different word forms and increases recall.
- **Example:**
```
"running", "ran", "runs" → "run"
```

## Information Need:


## Notas relatorio
- results- graficos sobre a avaiacao e observaçoes sobre os resultados