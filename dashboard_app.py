# dashboard_app.py (Streamlit ile canl"+/- performans kontrol paneli)
import kiripto_nova.streamlitst
import kiripto_nova.pandaspd
import kiripto_nova.sqlite3
import matplotlib.pyplot as plt

DB_NAME = "trade_history.db"

st.set_page_config(page_title="Kripto Bot Paneli", layout="wide")
st.title("?Y  Otomatik Kripto Bot Kontrol Paneli")

@st.cache_data()
def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM trades ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def draw_cumulative(df):
    df = df.sort_values("timestamp")
    df["cumulative_pnl"] = df["pnl"].cumsum()
    st.subheader("?Y K1?4m1?4latif K?r/Zarar")
    st.line_chart(df.set_index("timestamp")["cumulative_pnl"])

def trade_table(df):
    st.subheader("?Y "?...Ylem Ge?mi...Yi")
    st.dataframe(df)

def stats(df):
    wins = df[df["result"] == "win"]
    losses = df[df["result"] == "loss"]
    winrate = len(wins) / len(df) * 100 if len(df) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam "?...Ylem", len(df))
    col2.metric("Winrate", f"{winrate:.2f}%")
    col3.metric("Net PnL", f"{df['pnl'].sum():.2f} USDT")


if __name__ == "__main__":
    try:
        df = load_data()
        stats(df)
        draw_cumulative(df)
        trade_table(df)
    except Exception as e:
        st.error("Veri y1?4klenemedi. L1?4tfen i...Ylem ge?mi...Yi olu...Yturdu"Yunuzdan emin olun.")
