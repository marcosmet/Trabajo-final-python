"""
main.py  —  Punto de entrada del gráfico BTC en tiempo real.

Uso
───
    python main.py                        # BTC/USDT en 1 minuto (por defecto)
    python main.py --symbol ETHUSDT       # Otro par
    python main.py --interval 5m          # Otra temporalidad
    python main.py --symbol BTCUSDT --interval 15m --limit 300

Temporalidades válidas de Binance
──────────────────────────────────
  1m  3m  5m  15m  30m  1h  2h  4h  6h  8h  12h  1d  3d  1w  1M
"""

import argparse
import finplot as fplt

from Binance.BinanceRest import BinanceRest
from Binance.BinanceWebSocket import BinanceWebSocket
from Data.KlineManager import KlineManager
from Graphics.CandleChart import CandleChart


# ──────────────────────────────────────────────────────────────
# Argumentos de línea de comandos
# ──────────────────────────────────────────────────────────────

def parsear_args():
    parser = argparse.ArgumentParser(
        description="Gráfico de velas BTC/USDT con indicadores en tiempo real."
    )
    parser.add_argument(
        "--symbol", default="BTCUSDT",
        help="Par de trading (default: BTCUSDT)"
    )
    parser.add_argument(
        "--interval", default="1m",
        help="Temporalidad: 1m 3m 5m 15m 30m 1h 4h 1d ... (default: 1m)"
    )
    parser.add_argument(
        "--limit", default=500, type=int,
        help="Velas históricas a cargar (default: 500, máx: 1000)"
    )
    return parser.parse_args()


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    args = parsear_args()

    symbol = args.symbol.upper()
    interval = args.interval
    limit = min(args.limit, 1000)

    print(f"\n{'─' * 40}")
    print(f"  Par       : {symbol}")
    print(f"  Intervalo : {interval}")
    print(f"  Histórico : {limit} velas")
    print(f"{'─' * 40}\n")

    # ── Manager ──────────────────────────────
    manager = KlineManager(max_velas=limit)

    # ── Histórico ────────────────────────────
    rest = BinanceRest()
    historico = rest.obtener_klines(symbol=symbol, interval=interval, limit=limit)
    manager.cargar_historico(historico)

    print(f"✔  Histórico cargado: {len(historico)} velas")

    # ── Gráfico ──────────────────────────────
    chart = CandleChart(symbol=symbol, interval=interval)
    chart.cargar(manager.dataframe())

    # ── Callback WebSocket ───────────────────
    def on_kline(kline, cerrada):
        manager.actualizar(kline)
        chart.refrescar(manager.dataframe())

        if cerrada:
            print(
                f"  CERRADA | {kline.open_time} | "
                f"O {kline.open:.2f}  H {kline.high:.2f}  "
                f"L {kline.low:.2f}  C {kline.close:.2f} | "
                f"Vol {kline.volume:.2f}"
            )

    # ── WebSocket ────────────────────────────
    ws = BinanceWebSocket(symbol=symbol, interval=interval, on_kline=on_kline)
    ws.iniciar()

    print("✔  WebSocket conectado\n")

    import inspect
    import finplot as fplt

    print(inspect.signature(fplt.candlestick_ochl))
    print(inspect.signature(fplt.volume_ocv))

    # ── Mostrar ──────────────────────────────
    fplt.show()


if __name__ == "__main__":
    main()