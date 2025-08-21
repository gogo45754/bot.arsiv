# NovaQuantX - RSI modülü (tick bazlı, ultra hassas)
from collections import deque

class TickRSI:
    def __init__(self, period=14):
        self.period = period
        self.gains = deque(maxlen=period)
        self.losses = deque(maxlen=period)
        self.last_price = None
        self.rsi = None

    def update(self, price: float):
        if self.last_price is None:
            self.last_price = price
            return None

        delta = price - self.last_price
        self.last_price = price

        gain = max(delta, 0)
        loss = max(-delta, 0)

        self.gains.append(gain)
        self.losses.append(loss)

        if len(self.gains) < self.period:
            return None  # Yeterli veri yok

        avg_gain = sum(self.gains) / self.period
        avg_loss = sum(self.losses) / self.period

        if avg_loss == 0:
            self.rsi = 100
        else:
            rs = avg_gain / avg_loss
            self.rsi = 100 - (100 / (1 + rs))

        return round(self.rsi, 2)