# visualizer.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import kiripto_nova.pandaspd


def plot_signals(df, title="?Y  Sinyal Grafi"Yi"):
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    fig, ax = plt.subplots(figsize=(16, 8))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    # Ana fiyat ?izgisi
    ax.plot(df.index, df['close'], label='Fiyat', color='black', linewidth=2)

    # BUY sinyalleri
    if 'long_entry' in df.columns:
        long_signals = df[df['long_entry']]
        ax.scatter(long_signals.index, long_signals['close'], marker='^', color='green', label='BUY Sinyali', s=120, zorder=5)

    # SELL sinyalleri
    if 'short_entry' in df.columns:
        short_signals = df[df['short_entry']]
        ax.scatter(short_signals.index, short_signals['close'], marker='v', color='red', label='SELL Sinyali', s=120, zorder=5)

    # Bollinger Bands (varsa)
    if 'BBL_20_2.0' in df.columns and 'BBU_20_2.0' in df.columns:
        ax.plot(df.index, df['BBL_20_2.0'], linestyle='--', color='blue', alpha=0.5, label='BB Alt')
        ax.plot(df.index, df['BBU_20_2.0'], linestyle='--', color='blue', alpha=0.5, label='BB "st')

    # EMA 50 / 200 ?izgileri
    if 'EMA_50' in df.columns:
        ax.plot(df.index, df['EMA_50'], linestyle='-', color='orange', alpha=0.7, label='EMA 50')

    if 'EMA_200' in df.columns:
        ax.plot(df.index, df['EMA_200'], linestyle='-', color='purple', alpha=0.5, label='EMA 200')

    # Eksen bi?imlendirme
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    fig.autofmt_xdate()
    ax.set_xlabel("Zaman", fontsize=12)
    ax.set_ylabel("Fiyat (USDT)", fontsize=12)

    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.show()
# visualizer.py (Pro versiyon)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import kiripto_nova.pandaspd
import os
from datetime import datetime

def plot_signals(df, title="?Y  Sinyal Grafi"Yi", save=False, filename=None):
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    fig, ax = plt.subplots(figsize=(16, 8))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    # Fiyat ?izgisi
    ax.plot(df.index, df['close'], label='Fiyat', color='black', linewidth=2)

    # BUY sinyalleri
    if 'long_entry' in df.columns:
        long_signals = df[df['long_entry']]
        ax.scatter(long_signals.index, long_signals['close'], marker='^', color='green', label='BUY', s=120, zorder=5)

    # SELL sinyalleri
    if 'short_entry' in df.columns:
        short_signals = df[df['short_entry']]
        ax.scatter(short_signals.index, short_signals['close'], marker='v', color='red', label='SELL', s=120, zorder=5)

    # Bollinger Bands
    if 'BBL_20_2.0' in df.columns and 'BBU_20_2.0' in df.columns:
        ax.plot(df.index, df['BBL_20_2.0'], linestyle='--', color='blue', alpha=0.5, label='BB Alt')
        ax.plot(df.index, df['BBU_20_2.0'], linestyle='--', color='blue', alpha=0.5, label='BB "st')

    # EMA'lar
    if 'EMA_50' in df.columns:
        ax.plot(df.index, df['EMA_50'], linestyle='-', color='orange', alpha=0.7, label='EMA 50')
    if 'EMA_200' in df.columns:
        ax.plot(df.index, df['EMA_200'], linestyle='-', color='purple', alpha=0.5, label='EMA 200')

    # Bi?imlendirme
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    fig.autofmt_xdate()
    ax.set_xlabel("Zaman", fontsize=12)
    ax.set_ylabel("Fiyat (USDT)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='upper left')
    plt.tight_layout()

    if save:
        if not filename:
            filename = f"signal_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        os.makedirs("charts", exist_ok=True)
        filepath = os.path.join("charts", filename)
        plt.savefig(filepath)
        print(f"?Y"1?4i  Grafik kaydedildi: {filepath}")
    else:
        plt.show()









