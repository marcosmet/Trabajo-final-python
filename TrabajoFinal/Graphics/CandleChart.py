"""
CandleChart  —  Gráfico de velas japonesas con indicadores.

Diseño de paneles
─────────────────
  row=1  →  Precio + EMA20 + EMA50 + Bandas Bollinger + VWAP
  row=2  →  Volumen
  row=3  →  RSI (14)
  row=4  →  MACD (histograma + líneas)
"""

import pandas as pd
import finplot as fplt

from Indicators.indicadores import ema, rsi, vwap, bollinger, macd

# ─────────────────────────────────────────
# Paleta de colores
# ─────────────────────────────────────────

COLOR_VELA_ALCISTA = "#26a69a"  # verde azulado
COLOR_VELA_BAJISTA = "#ef5350"  # rojo
COLOR_EMA_20 = "#f6c90e"  # amarillo
COLOR_EMA_50 = "#ff9800"  # naranja
COLOR_BOLL_MEDIA = "#90caf9"  # azul claro
COLOR_BOLL_BANDA = "#546e7a"  # gris azulado
COLOR_VWAP = "#ce93d8"  # lila
COLOR_RSI = "#80cbc4"
COLOR_RSI_OB = "#ef5350"  # sobrecompra
COLOR_RSI_OS = "#26a69a"  # sobreventa
COLOR_MACD_LINEA = "#42a5f5"
COLOR_MACD_SEÑAL = "#ff7043"
COLOR_HIST_ALCISTA = "#26a69a"
COLOR_HIST_BAJISTA = "#ef5350"


class CandleChart:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval
        self._crear_layout()

        # Referencias a los plots para poder actualizarlos
        self._plot_velas = None
        self._plot_vol = None
        self._plot_ema20 = None
        self._plot_ema50 = None
        self._plot_boll_med = None
        self._plot_boll_sup = None
        self._plot_boll_inf = None
        self._plot_vwap = None
        self._plot_rsi = None
        self._plot_rsi_ob = None  # línea sobrecompra
        self._plot_rsi_os = None  # línea sobreventa
        self._plot_macd_lin = None
        self._plot_macd_sig = None
        self._plot_macd_his = None

    # ─────────────────────────────────────────
    # Layout
    # ─────────────────────────────────────────

    def _crear_layout(self):
        self.ax_precio, self.ax_vol, self.ax_rsi, self.ax_macd = fplt.create_plot(
            f"{self.symbol}  •  {self.interval}",
            rows=4,
            init_zoom_periods=120
        )

        # Accedemos a la ventana principal de finplot
        win = fplt.windows[0]

        # .ci (Central Item) contiene el QGraphicsGridLayout real de los gráficos
        win.ci.layout.setRowStretchFactor(0, 65)  # Fila 0: Precio (65%)
        win.ci.layout.setRowStretchFactor(1, 15)  # Fila 1: Volumen (15%)
        win.ci.layout.setRowStretchFactor(2, 10)  # Fila 2: RSI (10%)
        win.ci.layout.setRowStretchFactor(3, 10)  # Fila 3: MACD (10%)

    # ─────────────────────────────────────────
    # Carga inicial
    # ─────────────────────────────────────────

    def cargar(self, df: pd.DataFrame):
        if df.empty:
            return

        self._dibujar_velas(df)
        self._dibujar_volumen(df)
        self._dibujar_emas(df)
        self._dibujar_bollinger(df)
        self._dibujar_vwap(df)
        self._dibujar_rsi(df)
        self._dibujar_macd(df)

    # ─────────────────────────────────────────
    # Refresco en tiempo real
    # ─────────────────────────────────────────

    def refrescar(self, df: pd.DataFrame):
        if df.empty or self._plot_velas is None:
            return

        # Velas
        self._plot_velas.update_data(self._ochl(df))

        # Volumen
        self._plot_vol.update_data(df["Volume"])

        # EMAs
        self._plot_ema20.update_data(ema(df, 20))
        self._plot_ema50.update_data(ema(df, 50))

        # Bollinger
        med, sup, inf = bollinger(df)
        self._plot_boll_med.update_data(med)
        self._plot_boll_sup.update_data(sup)
        self._plot_boll_inf.update_data(inf)

        # VWAP
        self._plot_vwap.update_data(vwap(df))

        # RSI
        self._plot_rsi.update_data(rsi(df))

        # MACD
        lin, sig, his = macd(df)
        self._plot_macd_lin.update_data(lin)
        self._plot_macd_sig.update_data(sig)
        self._plot_macd_his.update_data(his)

        fplt.refresh()

    # ─────────────────────────────────────────
    # Helpers de dibujo
    # ─────────────────────────────────────────

    @staticmethod
    def _ochl(df: pd.DataFrame) -> pd.DataFrame:
        """Convierte OHLCV → OCHL (formato requerido por finplot)."""
        return df[["Open", "Close", "High", "Low"]]

    def _dibujar_velas(self, df):
        self._plot_velas = fplt.candlestick_ochl(
            self._ochl(df),
            ax=self.ax_precio,
            #candle_bull_color=COLOR_VELA_ALCISTA,
            #candle_bear_color=COLOR_VELA_BAJISTA,
        )

    def _dibujar_volumen(self, df):
        self._plot_vol = fplt.volume_ocv(
            df[["Open", "Close", "Volume"]],
            ax=self.ax_vol,
            #candle_bull_color=COLOR_VELA_ALCISTA + "aa",
            #candle_bear_color=COLOR_VELA_BAJISTA + "aa",
        )

    def _dibujar_emas(self, df):
        self._plot_ema20 = fplt.plot(
            ema(df, 20),
            ax=self.ax_precio,
            color=COLOR_EMA_20,
            legend="EMA 20",
            width=1,
        )
        self._plot_ema50 = fplt.plot(
            ema(df, 50),
            ax=self.ax_precio,
            color=COLOR_EMA_50,
            legend="EMA 50",
            width=1,
        )

    def _dibujar_bollinger(self, df):
        med, sup, inf = bollinger(df)

        self._plot_boll_med = fplt.plot(
            med, ax=self.ax_precio,
            color=COLOR_BOLL_MEDIA, legend="BB media",
            width=1, style="--",
        )
        self._plot_boll_sup = fplt.plot(
            sup, ax=self.ax_precio,
            color=COLOR_BOLL_BANDA, legend="BB sup",
            width=1,
        )
        self._plot_boll_inf = fplt.plot(
            inf, ax=self.ax_precio,
            color=COLOR_BOLL_BANDA, legend="BB inf",
            width=1,
        )

    def _dibujar_vwap(self, df):
        self._plot_vwap = fplt.plot(
            vwap(df),
            ax=self.ax_precio,
            color=COLOR_VWAP,
            legend="VWAP",
            width=2,
        )

    def _dibujar_rsi(self, df):
        serie_rsi = rsi(df)

        self._plot_rsi = fplt.plot(
            serie_rsi, ax=self.ax_rsi,
            color=COLOR_RSI, legend="RSI 14",
            width=1,
        )

        # Líneas horizontales de referencia
        fplt.add_line(
            (serie_rsi.index[0], 70),
            (serie_rsi.index[-1], 70),
            color=COLOR_RSI_OB, style="--", ax=self.ax_rsi,
        )
        fplt.add_line(
            (serie_rsi.index[0], 30),
            (serie_rsi.index[-1], 30),
            color=COLOR_RSI_OS, style="--", ax=self.ax_rsi,
        )

    def _dibujar_macd(self, df):
        lin, sig, his = macd(df)

        self._plot_macd_his = fplt.bar(
            his,
            ax=self.ax_macd,
            colorfunc=fplt.strength_colorfilter,
        )
        self._plot_macd_lin = fplt.plot(
            lin, ax=self.ax_macd,
            color=COLOR_MACD_LINEA, legend="MACD",
            width=1,
        )
        self._plot_macd_sig = fplt.plot(
            sig, ax=self.ax_macd,
            color=COLOR_MACD_SEÑAL, legend="Señal",
            width=1,
        )
