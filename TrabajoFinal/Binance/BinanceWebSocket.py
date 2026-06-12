import json
import websocket
import threading

from Models.Vela import Kline
from datetime import datetime


class BinanceWebSocket:

    def __init__(self, symbol, interval, on_kline):

        self.symbol = symbol.lower()
        self.interval = interval
        self.on_kline = on_kline

    def iniciar(self):

        socket = (
            f"wss://stream.binance.com:9443/ws/"
            f"{self.symbol}@kline_{self.interval}"
        )

        self.ws = websocket.WebSocketApp(
            socket,
            on_message=self._on_message
        )

        hilo = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )

        hilo.start()

    def _on_message(self, ws, message):

        data = json.loads(message)

        k = data["k"]

        kline = Kline(
            open_time=datetime.fromtimestamp(k["t"] / 1000),

            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"]),

            volume=float(k["v"])
        )

        cerrada = k["x"]

        self.on_kline(
            kline,
            cerrada
        )