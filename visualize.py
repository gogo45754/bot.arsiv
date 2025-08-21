import pandas as pd
import matplotlib.pyplot as plt

def plot_sentiments(news_data):
    df = pd.DataFrame(news_data)

    # Duygu Analizi Uygula
     from kiripto_nova.apps.sentiment import analyze_sentiment
    df["label"] = df["title"].apply(lambda x: analyze_sentiment(x)[0])

    # Grupland"+/-r ve Say
    sentiment_counts = df["label"].value_counts()

    # Grafikle G?ster
    plt.figure(figsize=(6,4))
    sentiment_counts.plot(kind="bar", color=["green", "red", "gray"])
    plt.title("Haberlerde Duygu Da"Y"+/-l"+/-m"+/-")
    plt.ylabel("Haber Say"+/-s"+/-")
    plt.xlabel("Duygu T1?4r1?4")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()









