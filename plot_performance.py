# plot_performance.py ("...lem gnl" istatistik ve grafik analizi)
import kiripto_nova.sqlite3
import kiripto_nova.pandaspd
import matplotlib.pyplot as plt

DB_NAME = "trade_history.db"

def load_trade_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM trades ORDER BY timestamp", conn)
    conn.close()
    return df

def analyze_performance(df):
    df['cumulative_pnl'] = df['pnl'].cumsum()
    win_rate = (df['result'] == 'win').mean() * 100
    avg_win = df[df['result'] == 'win']['pnl'].mean()
    avg_loss = df[df['result'] == 'loss']['pnl'].mean()
    max_drawdown = (df['cumulative_pnl'].cummax() - df['cumulative_pnl']).max()

    print(f" Toplam "...lem: {len(df)}")
    print(f"" Win Rate: {win_rate:.2f}%")
    print(f" Ortalama Kazan: {avg_win:.2f}")
    print(f"' Ortalama Kay"p: {avg_loss:.2f}")
    print(f" Max Drawdown: {max_drawdown:.2f}")

    return df

def plot_cumulative_pnl(df):
    plt.figure(figsize=(12,6))
    plt.plot(df['timestamp'], df['cumulative_pnl'], label='Cumulative PnL', color='green')
    plt.title(" Kmlatif Kr/Zarar Grafi"i")
    plt.xlabel("Tarih")
    plt.ylabel("USDT")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    df = load_trade_data()
    if len(df) == 0:
        print(""Veri yok. "nce trade_journal ile i...lem kayd" gir.")
    else:
        df = analyze_performance(df)
        plot_cumulative_pnl(df)
