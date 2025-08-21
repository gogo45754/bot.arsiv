import pandas as pd
import matplotlib.pyplot as plt

def plot_signal_results(csv_file="data/signal_log.csv"):
    df = pd.read_csv(csv_file, names=["signal", "score", "result"])
    success_rate = df["result"].value_counts(normalize=True) * 100
    success_rate.plot(kind="bar", color=["green", "red"])
    plt.title("Sinyal Ba...Yar"+/- Oran"+/-")
    plt.ylabel("%")
    plt.tight_layout()
    plt.show()
