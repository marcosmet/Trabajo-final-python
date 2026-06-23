import argparse
import threading
import sys

import finplot as fplt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QObject, pyqtSignal  # Importamos herramientas de hilos de Qt

from Binance.BinanceRest import BinanceRest
from Binance.BinanceWebSocket import BinanceWebSocket
from Data.KlineManager import KlineManager
from Graphics.CandleChart import CandleChart
from Graphics.ControlPanel import ControlPanel


# ─────────────────────────────────────────────────────────────
# Comunicador Seguro entre Hilos (Bridge)
# ─────────────────────────────────────────────────────────────
class MainSignaler(QObject):
    """Canal seguro para enviar datos de hilos de red al hilo principal de la UI."""
    kline_recibido = pyqtSignal(object, bool)  # Envía (kline, cerrada)
    reload_completo = pyqtSignal()  # Avisa que terminó la descarga REST


def parsear_args():
    p = argparse.ArgumentParser(description="BTC Chart — tiempo real")
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interval", default="1m")
    p.add_argument("--limit", default=500, type=int)
    return p.parse_args()


class App:

    def __init__(self, symbol, interval, limit):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit

        self.rest = BinanceRest()
        self.manager = KlineManager(max_velas=limit)
        self.ws = None
        self.chart = None
        self.panel = None

        # Instanciar el señalador y conectar eventos al hilo principal
        self.signaler = MainSignaler()
        self.signaler.kline_recibido.connect(self._on_kline_gui)
        self.signaler.reload_completo.connect(self._on_reload_gui)

    def iniciar(self):
        self._cargar_historico()

        # Gráfico — create_plot debe ir DESPUÉS de QApplication
        self.chart = CandleChart(symbol=self.symbol, interval=self.interval)
        self.chart.cargar(self.manager.dataframe())

        # Panel flotante
        self.panel = ControlPanel()
        self.panel.set_intervalo(self.interval)
        self.panel.show()

        # Señales del Panel
        self.panel.señales.toggle_indicador.connect(self._on_toggle)
        self.panel.señales.cambiar_temporalidad.connect(self._on_cambiar_temporalidad)

        # WebSocket
        self._iniciar_ws()

        print("✔  Listo — panel de control activo\n")
        fplt.show()

    def _cargar_historico(self):
        print(f"  Cargando {self.symbol} / {self.interval} …")
        historico = self.rest.obtener_klines(
            symbol=self.symbol,
            interval=self.interval,
            limit=self.limit
        )
        self.manager = KlineManager(max_velas=self.limit)
        self.manager.cargar_historico(historico)
        print(f"  ✔  {len(historico)} velas cargadas")

    def _iniciar_ws(self):
        if self.ws:
            self.ws.detener()

        self.ws = BinanceWebSocket(
            symbol=self.symbol,
            interval=self.interval,
            on_kline=self._on_kline
        )
        self.ws.iniciar()

        if self.panel:
            self.panel.set_estado("● Conectado", "#3fb950")

    # ── Manejo de Datos en Tiempo Real (Multithread Safe) ──

    def _on_kline(self, kline, cerrada):
        """Callback del WebSocket. Corre en un hilo SECUNDARIO de red. No toca la UI."""
        self.signaler.kline_recibido.emit(kline, cerrada)

    def _on_kline_gui(self, kline, cerrada):
        """Se ejecuta puramente en el HILO PRINCIPAL. Aquí es seguro actualizar la gráfica."""
        self.manager.actualizar(kline)
        self.chart.refrescar(self.manager.dataframe())

        if cerrada:
            print(
                f"  ✦ {kline.open_time} | "
                f"O {kline.open:.2f}  H {kline.high:.2f}  "
                f"L {kline.low:.2f}  C {kline.close:.2f}"
            )

    def _on_toggle(self, nombre: str, activo: bool):
        if self.chart:
            self.chart.toggle(nombre, activo)

    def _on_cambiar_temporalidad(self, symbol: str, interval: str):
        if symbol == self.symbol and interval == self.interval:
            return

        print(f"\n  Cambiando a {symbol} / {interval} …")

        if self.panel:
            self.panel.set_estado("⟳ Recargando…", "#e3b341")

        if self.ws:
            self.ws.detener()

        self.symbol = symbol
        self.interval = interval

        def _reload():
            # La descarga REST bloqueante se ejecuta fuera de la UI para que no se congele la app
            self._cargar_historico()
            # Notificamos de forma segura al hilo principal para redesplegar el gráfico
            self.signaler.reload_completo.emit()

        threading.Thread(target=_reload, daemon=True).start()

    def _on_reload_gui(self):
        """Actualizaciones de UI tras cambiar de temporalidad (Hilo Principal)."""
        self.chart.cambiar_titulo(self.symbol, self.interval)
        self.chart.refrescar(self.manager.dataframe())
        self._iniciar_ws()


def main():
    args = parsear_args()

    symbol = args.symbol.upper()
    interval = args.interval
    limit = min(args.limit, 1000)

    print(f"\n{'─' * 42}")
    print(f"  BTC Chart  —  tiempo real con indicadores")
    print(f"{'─' * 42}")
    print(f"  Par       : {symbol}")
    print(f"  Intervalo : {interval}")
    print(f"  Histórico : {limit} velas")
    print(f"{'─' * 42}\n")

    # QApplication DEBE existir antes de cualquier widget Qt
    qapp = QApplication.instance() or QApplication(sys.argv)

    app = App(symbol=symbol, interval=interval, limit=limit)
    app.iniciar()


if __name__ == "__main__":
    main()