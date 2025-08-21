import pandas as pd
import matplotlib.pyplot as plt

def plot_signal_density(csv_file):
    df = pd.read_csv(csv_file)
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    df['hour'] = df['publishedAt'].dt.hour
    df['signal'] = df['signal'].fillna("BEKLE")

    signal_counts = df.groupby(['hour', 'signal']).size().unstack(fill_value=0)
    signal_counts.plot(kind='bar', stacked=True)
    plt.title("Saat Bazl"+/- Sinyal Yo"Yunlu"Yu")
    plt.xlabel("Saat")
    plt.ylabel("Sinyal Say"+/-s"+/-")
    plt.tight_layout()
    plt.show()
