import requests
from datetime import datetime

from Models.Vela import Kline


class BinanceRest:
    BASE_URL = "https://api.binance.com"

    def obtener_klines(
            self,
            symbol="BTCUSDT",
            interval="1m",
            limit=500):
        url = f"{self.BASE_URL}/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        klines = []

        for row in data:
            kline = Kline(
                open_time=datetime.fromtimestamp(row[0] / 1000),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5])
            )

            klines.append(kline)

        return klines

    def obtener_precio_actual(self, symbol="BTCUSDT"):
        """Devuelve el último precio de mercado."""
        url = f"{self.BASE_URL}/api/v3/ticker/price"
        response = requests.get(url, params={"symbol": symbol})
        response.raise_for_status()
        return float(response.json()["price"])