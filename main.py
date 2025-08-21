import os, time, logging
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Binance API
from services.binance_client import get_client
from strategies.basic_macd_rsi import generate_signal
from core.trade_executor import place_order

# Haber ve duygu analizi
from kiripto_nova.signals.get_news import get_crypto_news
 from kiripto_nova.apps.sentiment import analyze_sentiment
 from kiripto_nova.apps.explainer import explain_signal
 from kiripto_nova.apps.csv_writer import save_to_csv
from kiripto_nova.apps.telegram_bot import send_signal_to_telegram
from kiripto_nova.signals.signal_tracker import analyze_signal_effect
from dashboard.visual_panel import dashboard_view

# Strateji filtreleri ve yöneticiler
from regime import regime
from cooldown import cooldown
from kiripto_nova.execution.position_manager import pos_mgr
from atr import atr_levels
from kiripto_nova.ai.ml_engine import ml_engine
from ta_engine import ta_engine
from news_engine import news_engine

# Log yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Ortam değişkenleri
load_dotenv(dotenv_path="my_env_file.env")
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
client = get_client()

def fetch_data(symbol: str, limit: int = 100) -> pd.DataFrame:
    try:
        ohlcv = client.fetch_ohlcv(symbol, timeframe="5m", limit=limit)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except Exception as e:
        logging.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame()

def run_news_analysis():
    news_data = get_crypto_news()
    signals = []

    for news in news_data:
        title = news.get("title", "")
        description = news.get("description", "")
        label, score = analyze_sentiment(f"{title} {description}")

        if label == "positive" and score > 0.7:
            signal = "AL"
        elif label == "negative" and score > 0.6:
            signal = "SAT"
        else:
            signal = "BEKLE"

        note = explain_signal(title, description)
        send_signal_to_telegram(title, signal, score)

        signals.append({
            "title": title,
            "signal": signal,
            "sentiment": label,
            "score": round(score, 3),
            "note": note
        })

    save_to_csv(signals)
    logging.info(f"{len(signals)} haber sinyali işlendi ve kaydedildi.")

def run_trading_cycle(symbol="DOGE/USDT"):
    df = fetch_data(symbol)
    if df.empty:
        logging.warning("Veri alınamadı, işlem döngüsü atlandı.")
        return

    ta_sig = ta_engine.decide(df)
    ml_sig = ml_engine.decide(df)
    news = news_engine.bias()
    tdrdir, vol = regime.allow(df)
    cooldown.tick()

    direction, entry, conf = None, None, 0.5

    if ta_sig:
        direction, entry = ta_sig
        if ml_sig and ml_sig[0] == direction: conf += 0.2 * ml_sig[1]
        if news and news[0] == direction: conf += 0.2 * news[1]

        if tdrdir == 1 and direction in ["LONG", "SHORT"]: conf -= 0.3
        if vol[df['close'].pct_change().rolling(36).std().median()]: conf -= 0.1

        if conf >= 0.65 and cooldown.ok() and pos_mgr.can_open(direction):
            sl, tp = atr_levels(df, entry, direction)
            place_order({"direction": direction, "entry": entry, "sl": sl, "tp": tp})
            pos_mgr.on_open(direction)
            cooldown.trigger()
            logging.info(f"✅ İşlem açıldı: {direction} @ {entry} | SL: {sl} | TP: {tp}")
        else:
            logging.info("⏳ Sinyal yeterince güçlü değil veya pozisyon açılamaz.")
    else:
        logging.info("❌ Teknik sinyal bulunamadı.")

def main():
    logging.info("🚀 Nova Chain Komuta Sistemi vX.1 başlatılıyor...")
    run_news_analysis()

    while True:
        run_trading_cycle()
        effect = analyze_signal_effect("DOGE", datetime.utcnow().isoformat())
        logging.info(f"📊 Sinyal etkisi: {effect}")
        dashboard_view()
        time.sleep(60)

if __name__ == "__main__":
    main()