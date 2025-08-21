# NovaQuantX - Ticaret Motoru (pozisyon yönetimi + sinyal işleme)
from dataclasses import dataclass

@dataclass
class Position:
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    leverage: int
    qty: float
    open_ts: int

class NovaTrader:
    def __init__(self, leverage=10, rsi_buy=30, rsi_sell=70):
        self.positions = {}
        self.leverage = leverage
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def process_signal(self, symbol: str, price: float, rsi: float, ts: int):
        pos = self.positions.get(symbol)

        # LONG sinyali
        if rsi <= self.rsi_buy and pos is None:
            qty = self.calculate_qty(price)
            self.positions[symbol] = Position(
                symbol=symbol,
                side='LONG',
                entry_price=price,
                leverage=self.leverage,
                qty=qty,
                open_ts=ts
            )
            print(f"🟢 LONG açıldı: {symbol} @ {price:.2f} x{self.leverage}")

        # SHORT sinyali
        elif rsi >= self.rsi_sell and pos is None:
            qty = self.calculate_qty(price)
            self.positions[symbol] = Position(
                symbol=symbol,
                side='SHORT',
                entry_price=price,
                leverage=self.leverage,
                qty=qty,
                open_ts=ts
            )
            print(f🔴 SHORT açıldı: {symbol} @ {price:.2f} x{self.leverage}")

        # Pozisyon kapatma mantığı (örnek: RSI nötr bölgeye girerse)
        elif pos:
            if (pos.side == 'LONG' and rsi >= 50) or (pos.side == 'SHORT' and rsi <= 50):
                pnl = self.calculate_pnl(pos, price)
                print(f"⚪ Pozisyon kapandı: {symbol} {pos.side} PnL={pnl:.2f}")
                del self.positions[symbol]

    def calculate_qty(self, price: float):
        capital = 100  # sabit sermaye (örnek)
        return (capital * self.leverage) / price

    def calculate_pnl(self, pos: Position, current_price: float):
        if pos.side == 'LONG':
            return (current_price - pos.entry_price) * pos.qty
        else:
            return (pos.entry_price - current_price) * pos.qty