import json
import websocket
import threading

from Models.Vela import Kline
from datetime import datetime


class BinanceWebSocket:
    """
    Conecta a los streams combinados de Binance para un símbolo dado.
    Escucha tanto las velas (klines) como el Order Flow en vivo (aggTrade).
    """

    def __init__(self, symbol, interval, on_kline, on_trade=None):
        self.symbol = symbol.lower()
        self.interval = interval
        self.on_kline = on_kline
        self.on_trade = on_trade  # ◄ NUEVO: Callback para la cinta de órdenes
        self.ws = None

    def iniciar(self):
        # Definimos los dos canales que queremos escuchar
        stream_kline = f"{self.symbol}@kline_{self.interval}"
        stream_trade = f"{self.symbol}@aggTrade"

        # ◄ NUEVO: Usamos la URL de streams combinados de Binance (?streams=...)
        socket = (
            f"wss://stream.binance.com:9443/stream?streams="
            f"{stream_kline}/{stream_trade}"
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
        mensaje = json.loads(message)

        # En streams combinados, el payload real viene dentro de la llave "data"
        stream = mensaje.get("stream")
        data = mensaje.get("data")

        if not stream or not data:
            return

        # 1. Procesar actualización de Velas (Klines)
        if "kline" in stream:
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
            if self.on_kline:
                self.on_kline(kline, cerrada)

        # 2. Procesar nueva Orden de Mercado (Order Flow / Tape)
        elif "aggTrade" in stream:
            if self.on_trade:
                # Pasamos los datos crudos del trade a la interfaz
                self.on_trade(data)

    def _on_error(self, ws, error):
        print(f"[WebSocket] Error: {error}")

    def _on_close(self, ws, code, msg):
        print(f"[WebSocket] Cerrado — código: {code}")