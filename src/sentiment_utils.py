import os
from typing import Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# optional emotion libraries (NRCLex or text2emotion)
try:
    from nrclex import NRCLex  # type: ignore
    _HAS_NR_CLEX = True
except Exception:
    NRCLex = None  # type: ignore
    _HAS_NR_CLEX = False

try:
    import text2emotion as te  # type: ignore
    _HAS_TEXT2EMOTION = True
except Exception:
    te = None  # type: ignore
    _HAS_TEXT2EMOTION = False


def analyze_song_sentiments(
    input_csv: str,
    text_column: str = "song_lyrics",
    output_plot: Optional[str] = None,
    show_plot: bool = False,
) -> Tuple[pd.DataFrame, plt.Figure]:


    # Verificações iniciais
    abs_path = os.path.abspath(input_csv)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Ficheiro não encontrado: {abs_path}")

    if os.path.getsize(abs_path) == 0:
        raise ValueError(f"Ficheiro '{abs_path}' está vazio.")

    # Ler CSV (detecta separador padrão, permite erro claro)
    try:
        df = pd.read_csv(abs_path)
    except Exception as e:
        raise ValueError(f"Erro ao ler CSV '{abs_path}': {e}")

    if text_column not in df.columns:
        raise ValueError(f"Coluna '{text_column}' não encontrada no CSV. Colunas disponíveis: {list(df.columns)}")

    # Preparar NLTK VADER
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)

    sia = SentimentIntensityAnalyzer()

    # Calcular sentimento por linha
    def label_from_score(score: float) -> str:
        if score >= 0.05:
            return "positive"
        if score <= -0.05:
            return "negative"
        return "neutral"

    sentiments = []
    for i, text in enumerate(df[text_column].fillna("")):
        if not isinstance(text, str) or text.strip() == "":
            sentiments.append("neutral")
            continue
        try:
            score = sia.polarity_scores(text).get("compound", 0.0)
        except Exception:
            score = 0.0
        sentiments.append(label_from_score(score))

    df = df.copy()
    df["_sentiment"] = sentiments

    counts = df["_sentiment"].value_counts().reindex(["positive", "neutral", "negative"]).fillna(0).astype(int)
    sentiment_counts_df = counts.reset_index()
    sentiment_counts_df.columns = ["sentiment", "count"]

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {"positive": "#2ca02c", "neutral": "#7f7f7f", "negative": "#d62728"}
    sentiments_order = sentiment_counts_df["sentiment"].tolist()
    counts_order = sentiment_counts_df["count"].tolist()
    bar_colors = [colors.get(s, "#7f7f7f") for s in sentiments_order]

    ax.bar(sentiments_order, counts_order, color=bar_colors)
    ax.set_title("Distribuição de Sentimentos nas Músicas")
    ax.set_ylabel("Número de músicas")
    ax.set_xlabel("Sentimento")

    for i, v in enumerate(counts_order):
        ax.text(i, v + max(1, max(counts_order) * 0.01), str(v), ha="center")

    plt.tight_layout()

    if output_plot:
        try:
            fig.savefig(output_plot, dpi=150)
        except Exception as e:
            raise IOError(f"Falha ao guardar o ficheiro de imagem '{output_plot}': {e}")

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    return sentiment_counts_df, fig


def analyze_song_emotions(
    input_csv: str,
    text_column: str = "song_lyrics",
    output_plot: Optional[str] = None,
    engine: str = "nrclex",
    show_plot: bool = False,
) -> Tuple[pd.DataFrame, plt.Figure]:

    abs_path = os.path.abspath(input_csv)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Ficheiro não encontrado: {abs_path}")
    if os.path.getsize(abs_path) == 0:
        raise ValueError(f"Ficheiro '{abs_path}' está vazio.")

    try:
        df = pd.read_csv(abs_path)
    except Exception as e:
        raise ValueError(f"Erro ao ler CSV '{abs_path}': {e}")

    if text_column not in df.columns:
        raise ValueError(f"Coluna '{text_column}' não encontrada no CSV. Colunas disponíveis: {list(df.columns)}")

    # choose engine
    engine = engine.lower()
    if engine == "nrclex" and not _HAS_NR_CLEX:
        raise ImportError("NRCLex não está instalado. Instale com: pip install nrclex")
    if engine == "text2emotion" and not _HAS_TEXT2EMOTION:
        raise ImportError("text2emotion não está instalado. Instale com: pip install text2emotion")

    total_counts = {}

    for text in df[text_column].fillna(""):
        if not isinstance(text, str) or text.strip() == "":
            continue
        if engine == "nrclex":
            obj = NRCLex(text)
            # raw_emotion_scores é um dict {emotion: count}
            for emo, cnt in obj.raw_emotion_scores.items():
                total_counts[emo] = total_counts.get(emo, 0) + cnt
        else:
            # text2emotion retorna: {'Happy':0.0,...}
            emo_scores = te.get_emotion(text)
            for emo, score in emo_scores.items():
                # score é uma proporção; agregamos como soma de pontuações
                total_counts[emo.lower()] = total_counts.get(emo.lower(), 0.0) + float(score)

    # normalize text2emotion scores to counts-like numbers if needed
    if engine == "text2emotion":
        # convert to integer-like counts by scaling
        # multiply by 100 and round
        total_counts = {k: int(round(v * 100)) for k, v in total_counts.items()}

    if not total_counts:
        raise ValueError("Nenhuma emoção encontrada nos textos fornecidos.")

    # build DataFrame
    emo_items = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)
    emo_df = pd.DataFrame(emo_items, columns=["emotion", "count"])

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(emo_df['emotion'], emo_df['count'], color='#1f77b4')
    ax.set_title('Distribution of Emotions in Songs')
    ax.set_ylabel('Sum of Occurrences / Scores')
    ax.set_xlabel('Emotion')
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(emo_df['count']):
        ax.text(i, v + max(1, max(emo_df['count']) * 0.01), str(v), ha='center')
    plt.tight_layout()

    if output_plot:
        fig.savefig(output_plot, dpi=150)
    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    return emo_df, fig


if __name__ == "__main__":
    # Pequeno exemplo de uso quando executado diretamente
    import argparse

    parser = argparse.ArgumentParser(description="Analisar sentimentos em músicas e gerar gráfico")
    parser.add_argument("csv", help="CSV de entrada")
    parser.add_argument("--col", default="song_lyrics", help="Coluna com letras")
    parser.add_argument("--out", help="Caminho para salvar o gráfico (png)")
    parser.add_argument("--mode", choices=["polarity", "emotion"], default="polarity", help="'polarity' para positivo/negativo/neutro ou 'emotion' para emoções granulares")
    parser.add_argument("--engine", choices=["nrclex", "text2emotion"], default="nrclex", help="Motor de emoção a usar (quando --mode emotion)")
    args = parser.parse_args()

    if args.mode == "polarity":
        df_counts, _ = analyze_song_sentiments(args.csv, text_column=args.col, output_plot=args.out, show_plot=True)
        print(df_counts)
    else:
        emo_df, _ = analyze_song_emotions(args.csv, text_column=args.col, output_plot=args.out, engine=args.engine, show_plot=True)
        print(emo_df)
