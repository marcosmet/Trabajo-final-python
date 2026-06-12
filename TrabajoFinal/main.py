from Binance.BinanceRest import BinanceRest
from Binance.BinanceWebSocket import BinanceWebSocket

from Data.KlineManager import KlineManager

from Graphics.CandleChart import CandleChart

import finplot as fplt


# =====================================
# MANAGER
# =====================================

manager = KlineManager()


# =====================================
# HISTÓRICO
# =====================================

rest = BinanceRest()

historico = rest.obtener_klines(
    symbol="BTCUSDT",
    interval="1m",
    limit=500
)

manager.cargar_historico(historico)

print(
    f"Histórico cargado: {len(historico)} velas"
)


# =====================================
# GRÁFICO
# =====================================

chart = CandleChart()

chart.cargar(
    manager.dataframe()
)


# =====================================
# CALLBACK WEBSOCKET
# =====================================

def on_kline(kline, cerrada):

    manager.actualizar(kline)

    chart.refrescar(
        manager.dataframe()
    )

    if cerrada:

        print(
            f"VELA CERRADA | "
            f"{kline.open_time} | "
            f"Close: {kline.close}"
        )


# =====================================
# WEBSOCKET
# =====================================

ws = BinanceWebSocket(
    symbol="BTCUSDT",
    interval="1m",
    on_kline=on_kline
)

ws.iniciar()


# =====================================
# INICIAR FINPLOT
# =====================================

fplt.show()