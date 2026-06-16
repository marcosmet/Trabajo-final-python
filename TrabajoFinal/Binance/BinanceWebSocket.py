import json
import websocket
import threading

from Models.Vela import Kline
from datetime import datetime


class BinanceWebSocket:
    """
    Conecta al stream de klines de Binance para un símbolo e intervalo dados.
    Llama a `on_kline(kline, cerrada)` cada vez que llega una actualización.
    """

    def __init__(self, symbol, interval, on_kline):
        self.symbol = symbol.lower()
        self.interval = interval
        self.on_kline = on_kline
        self.ws = None

    def iniciar(self):
        socket = (
            f"wss://stream.binance.com:9443/ws/"
            f"{self.symbol}@kline_{self.interval}"
        )

        self.ws = websocket.WebSocketApp(
            socket,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        hilo = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )

        hilo.start()

    def detener(self):
        if self.ws:
            self.ws.close()

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

        self.on_kline(kline, cerrada)

    def _on_error(self, ws, error):
        print(f"[WebSocket] Error: {error}")

    def _on_close(self, ws, code, msg):
        print(f"[WebSocket] Cerrado — código: {code}")