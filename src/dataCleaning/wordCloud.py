import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS


def create_lyrics_wordcloud(csv_path, text_column='lyrics', output_file='lyrics_wordcloud.png'):
    """
    Create and display a word cloud from the song lyrics column in a CSV file.
    """
    df = pd.read_csv(csv_path)
    
    text = " ".join(str(lyric) for lyric in df[text_column].dropna())
    
    stopwords = set(STOPWORDS)
    stopwords.update([
        "am", "is", "are", "was", "be", "been", "being",
        "do", "does", "did", "doing",
        "have", "has", "had", "having",

        "put", "keep", "hold", "leave", "bring",
        "move", "run", "walk", "stand", "sit",
        "turn", "start", "stop", "work", "live",
        "look", "watch", "hear", "listen",
        "talk", "speak", "call", "try", "tryin",
        "help", "show", "find", "found",
        "lose", "lost", "stay", "play",
        "keep", "kept",

        "can", "cant", "could", "couldnt",
        "should", "shouldnt", "would", "wouldnt",
        "may", "might", "must",

        "feel", "felt", "seem", "seemed",
        "happen", "happens",

        "dont", "doesnt", "didnt",
        "isnt", "arent", "wasnt", "werent",
        "havent", "hasnt", "hadnt",
        "cant", "couldnt", "shouldnt",
        "wouldnt", "imma",

        "into", "onto", "upon", "through",
        "while", "without", "within",
        "cause", "cuz", "cos", "because",
        "maybe", "really", "just", "only",

        "ya", "yall", "huh", "hmm", "hahaha",
        "whoa", "woah", "uhhuh", "nah",

        "time", "times", "moment",
    ])

    
    wordcloud = WordCloud(width=1000, height=600,
                          background_color='white',
                          stopwords=stopwords,
                          collocations=False).generate(text)
    
    # Display and save
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud - Song Lyrics', fontsize=16)
    
    wordcloud.to_file(output_file)
    print(f"Saved lyrics word cloud as {output_file}")



def create_bio_wordcloud(csv_path, text_column='artist_bio', output_file='bio_wordcloud.png'):
    """
    Create and display a word cloud from the artist biography column in a CSV file.
    """
    df = pd.read_csv(csv_path)
    
    text = " ".join(str(bio) for bio in df[text_column].dropna())
    
    stopwords = set(STOPWORDS)
    stopwords.update([
        "am", "is", "are", "was", "be", "been", "being",
        "do", "does", "did", "doing",
        "have", "has", "had", "having",

        "put", "keep", "hold", "leave", "bring",
        "move", "run", "walk", "stand", "sit",
        "turn", "start", "stop", "work", "live",
        "look", "watch", "hear", "listen",
        "talk", "speak", "call", "try", "tryin",
        "help", "show", "find", "found",
        "lose", "lost", "stay", "play",
        "keep", "kept",

        "can", "cant", "could", "couldnt",
        "should", "shouldnt", "would", "wouldnt",
        "may", "might", "must",

        "feel", "felt", "seem", "seemed",
        "happen", "happens",

        "dont", "doesnt", "didnt",
        "isnt", "arent", "wasnt", "werent",
        "havent", "hasnt", "hadnt",
        "cant", "couldnt", "shouldnt",
        "wouldnt", "imma",

        "into", "onto", "upon", "through",
        "while", "without", "within",
        "cause", "cuz", "cos", "because",
        "maybe", "really", "just", "only",

        # Fillers comuns em música
        "ya", "yall", "huh", "hmm", "hahaha",
        "whoa", "woah", "uhhuh", "nah",

        # Tempo genérico (sem eliminar temas como "night" ou "morning")
        "time", "times", "moment",
    ])

        
    
    # Generate word cloud
    wordcloud = WordCloud(width=1000, height=600,
                          background_color='white',
                          stopwords=stopwords,
                          collocations=False).generate(text)
    
    # Display and save
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud - Artist Bio', fontsize=16)
    
    wordcloud.to_file(output_file)
    print(f"Saved bio word cloud as {output_file}")
    
    
create_lyrics_wordcloud('dataset/song.csv', text_column='song_lyrics')
create_bio_wordcloud('dataset/artist.csv', text_column='artist_bio')