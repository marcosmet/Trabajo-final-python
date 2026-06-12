import pandas as pd
import finplot as fplt


class CandleChart:

    def __init__(self):

        self.ax = fplt.create_plot(
            "BTCUSDT",
            rows=1
        )

        self.candle_plot = None

    def cargar(self, df):

        candles = pd.DataFrame()

        candles["Open"] = df["Open"]
        candles["Close"] = df["Close"]
        candles["High"] = df["High"]
        candles["Low"] = df["Low"]

        self.candle_plot = fplt.candlestick_ochl(
            candles,
            ax=self.ax
        )

    def refrescar(self, df):

        candles = pd.DataFrame()

        candles["Open"] = df["Open"]
        candles["Close"] = df["Close"]
        candles["High"] = df["High"]
        candles["Low"] = df["Low"]

        self.candle_plot.update_data(candles)

        fplt.refresh()