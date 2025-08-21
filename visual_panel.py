import pandas as pd
import matplotlib.pyplot as plt

def dashboard_view(csv_file="data/signal_log.csv"):
    df = pd.read_csv(csv_file, names=["signal", "score", "result"])

    # 1. Sinyal Da""l"m"
    signal_count = df["signal"].value_counts()
    signal_count.plot(kind="bar", title=" Sinyal Da""l"m"", color="steelblue")
    plt.ylabel("Adet")
    plt.tight_layout()
    plt.show()

    # 2. Ba...ar" Oran"
    result_count = df["result"].value_counts(normalize=True) * 100
    result_count.plot(kind="pie", title=" Ba...ar" Oran"", autopct="%.1f%%")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

    # 3. Skor Histogram"
    df["score"].plot(kind="hist", bins=10, title="" Sinyal Skor Yo"unlu"u", color="purple")
    plt.xlabel("Skor")
    plt.tight_layout()
    plt.show()










