import pandas as pd
import finplot as fplt

from Indicators.indicadores import ema, rsi, vwap, bollinger, macd


# ─────────────────────────────────────────────────────────────
# Paleta dark / Cyberpunk Profesional
# ─────────────────────────────────────────────────────────────

BG_DARK          = "#0d1117"
CYAN             = "#00e5ff"
MAGENTA          = "#ff00e5"
CYAN_VOL         = "#00e5ff55"
MAGENTA_VOL      = "#ff00e555"

COLOR_EMA_20     = "#f6c90e"
COLOR_EMA_50     = "#ff9800"
COLOR_BOLL_MEDIA = "#4fc3f7"
COLOR_BOLL_BANDA = "#37474f"
COLOR_VWAP       = "#ce93d8"
COLOR_RSI        = "#80cbc4"
COLOR_MACD_LIN   = "#42a5f5"
COLOR_MACD_SIG   = "#ff7043"


def _aplicar_tema_dark():
    fplt.foreground = "#c9d1d9"
    fplt.background = BG_DARK

    # ¡SOLUCIÓN! Evita que las filas impares (Volumen y MACD) se rendericen en blanco
    fplt.odd_plot_background = BG_DARK

    fplt.candle_bull_color      = CYAN
    fplt.candle_bear_color      = MAGENTA
    fplt.candle_bull_body_color = CYAN
    fplt.candle_bear_body_color = MAGENTA
    fplt.volume_bull_color      = CYAN_VOL
    fplt.volume_bear_color      = MAGENTA_VOL
    fplt.volume_bull_body_color = CYAN_VOL


_aplicar_tema_dark()


# ─────────────────────────────────────────────────────────────
# CandleChart
# ─────────────────────────────────────────────────────────────

class CandleChart:

    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.symbol   = symbol
        self.interval = interval
        self._df      = None

        # Estado de visibilidad inicial
        self._activo = {
            "ema20": False, "ema50": False,
            "bollinger": False, "vwap": False,
            "rsi": False, "macd": False,
            "volumen": True,
        }

        self._crear_layout()
        self._init_plots()

    # ── Layout ──────────────────────────────────────────

    def _crear_layout(self):
        self.ax_precio, self.ax_vol, self.ax_rsi, self.ax_macd = fplt.create_plot(
            f"{self.symbol}  ·  {self.interval}",
            rows=4,
            init_zoom_periods=120,
        )
        # El escalado inicial se computa dinámicamente al cargar

    def _init_plots(self):
        self._plot_velas    = None
        self._plot_vol      = None
        self._plot_ema20    = None
        self._plot_ema50    = None
        self._plot_boll_med = None
        self._plot_boll_sup = None
        self._plot_boll_inf = None
        self._plot_vwap     = None
        self._plot_rsi      = None
        self._plot_macd_lin = None
        self._plot_macd_sig = None
        self._plot_macd_his = None

    # ── Redimensión Dinámica de Paneles ──────────────────

    def _actualizar_layout(self):
        """Oculta paneles y colapsa los márgenes a 0 de forma dinámica."""
        if not fplt.windows:
            return
        win = fplt.windows[0]
        layout = win.ci.layout  # Layout nativo de Qt en finplot

        # Fila 0: Precios (Siempre activo)
        layout.setRowStretchFactor(0, 60)
        layout.setRowMinimumHeight(0, 150)

        # Fila 1: Volumen
        if self._activo["volumen"]:
            self.ax_vol.show()
            layout.setRowStretchFactor(1, 15)
            layout.setRowMinimumHeight(1, 40)
            layout.setRowSpacing(1, 5)
        else:
            self.ax_vol.hide()
            layout.setRowStretchFactor(1, 0)
            layout.setRowMinimumHeight(1, 0)
            layout.setRowSpacing(1, 0)

        # Fila 2: RSI
        if self._activo["rsi"]:
            self.ax_rsi.show()
            layout.setRowStretchFactor(2, 12)
            layout.setRowMinimumHeight(2, 50)
            layout.setRowSpacing(2, 5)
        else:
            self.ax_rsi.hide()
            layout.setRowStretchFactor(2, 0)
            layout.setRowMinimumHeight(2, 0)
            layout.setRowSpacing(2, 0)

        # Fila 3: MACD
        if self._activo["macd"]:
            self.ax_macd.show()
            layout.setRowStretchFactor(3, 13)
            layout.setRowMinimumHeight(3, 50)
            layout.setRowSpacing(3, 5)
        else:
            self.ax_macd.hide()
            layout.setRowStretchFactor(3, 0)
            layout.setRowMinimumHeight(3, 0)
            layout.setRowSpacing(3, 0)

        layout.activate()

    # ── Carga inicial ───────────────────────────────────

    def cargar(self, df: pd.DataFrame):
        if df.empty:
            return
        self._df = df
        self._dibujar_velas(df)
        self._dibujar_volumen(df)

        # Ajusta visibilidad según diccionario de estados iniciales
        self._actualizar_layout()

    # ── Refresco en tiempo real ─────────────────────────

    def refrescar(self, df: pd.DataFrame):
        if df.empty or self._plot_velas is None:
            return

        # Bloqueo opcional de scroll para que no te tire hacia adelante al actualizar
        try:
            xmin, xmax = self.ax_precio.vb.viewRange()[0]
            usuario_mirando_atras = (len(self._df) - xmax) > 5 if self._df is not None else False
        except Exception:
            usuario_mirando_atras = False

        self._df = df
        self._plot_velas.update_data(self._ochl(df))

        if self._plot_vol and self._activo["volumen"]:
            self._plot_vol.update_data(df[["Open", "Close", "Volume"]])

        if self._plot_ema20 and self._activo["ema20"]:
            self._plot_ema20.update_data(ema(df, 20))

        if self._plot_ema50 and self._activo["ema50"]:
            self._plot_ema50.update_data(ema(df, 50))

        if self._activo["bollinger"] and self._plot_boll_med:
            med, sup, inf = bollinger(df)
            self._plot_boll_med.update_data(med)
            self._plot_boll_sup.update_data(sup)
            self._plot_boll_inf.update_data(inf)

        if self._plot_vwap and self._activo["vwap"]:
            self._plot_vwap.update_data(vwap(df))

        if self._plot_rsi and self._activo["rsi"]:
            self._plot_rsi.update_data(rsi(df))

        if self._activo["macd"] and self._plot_macd_lin:
            lin, sig, his = macd(df)
            self._plot_macd_lin.update_data(lin)
            self._plot_macd_sig.update_data(sig)
            self._plot_macd_his.update_data(his)

        if usuario_mirando_atras:
            self.ax_precio.setXRange(xmin, xmax, padding=0)

        fplt.refresh()

    # ── Toggle desde las señales del ControlPanel ───────

    def toggle(self, nombre: str, activar: bool):
        self._activo[nombre] = activar
        df = self._df
        if df is None or df.empty:
            return

        if nombre == "ema20":
            self._simple_toggle("_plot_ema20", activar,
                lambda: fplt.plot(ema(df, 20), ax=self.ax_precio,
                                  color=COLOR_EMA_20, legend="EMA 20", width=1))

        elif nombre == "ema50":
            self._simple_toggle("_plot_ema50", activar,
                lambda: fplt.plot(ema(df, 50), ax=self.ax_precio,
                                  color=COLOR_EMA_50, legend="EMA 50", width=1))

        elif nombre == "bollinger":
            if activar:
                if not self._plot_boll_med:
                    med, sup, inf = bollinger(df)
                    self._plot_boll_med = fplt.plot(med, ax=self.ax_precio,
                        color=COLOR_BOLL_MEDIA, legend="BB media", width=1, style="--")
                    self._plot_boll_sup = fplt.plot(sup, ax=self.ax_precio,
                        color=COLOR_BOLL_BANDA, legend="BB sup", width=1)
                    self._plot_boll_inf = fplt.plot(inf, ax=self.ax_precio,
                        color=COLOR_BOLL_BANDA, legend="BB inf", width=1)
                else:
                    for p in (self._plot_boll_med, self._plot_boll_sup, self._plot_boll_inf):
                        p.show()
            else:
                for p in (self._plot_boll_med, self._plot_boll_sup, self._plot_boll_inf):
                    if p: p.hide()

        elif nombre == "vwap":
            self._simple_toggle("_plot_vwap", activar,
                lambda: fplt.plot(vwap(df), ax=self.ax_precio,
                                  color=COLOR_VWAP, legend="VWAP", width=2))

        elif nombre == "rsi":
            if activar:
                if not self._plot_rsi:
                    self._plot_rsi = fplt.plot(rsi(df), ax=self.ax_rsi,
                                               color=COLOR_RSI, legend="RSI 14", width=1)
                else:
                    self._plot_rsi.show()
            else:
                if self._plot_rsi: self._plot_rsi.hide()

        elif nombre == "macd":
            if activar:
                if not self._plot_macd_lin:
                    lin, sig, his = macd(df)
                    self._plot_macd_his = fplt.bar(his, ax=self.ax_macd,
                                                   colorfunc=fplt.strength_colorfilter)
                    self._plot_macd_lin = fplt.plot(lin, ax=self.ax_macd,
                                                    color=COLOR_MACD_LIN, legend="MACD", width=1)
                    self._plot_macd_sig = fplt.plot(sig, ax=self.ax_macd,
                                                    color=COLOR_MACD_SIG, legend="Señal", width=1)
                else:
                    for p in (self._plot_macd_his, self._plot_macd_lin, self._plot_macd_sig):
                        p.show()
            else:
                for p in (self._plot_macd_his, self._plot_macd_lin, self._plot_macd_sig):
                    if p: p.hide()

        elif nombre == "volumen":
            if self._plot_vol:
                self._plot_vol.show() if activar else self._plot_vol.hide()

        # Recalcula dimensiones de los paneles al cambiar estados
        self._actualizar_layout()
        fplt.refresh()

    def _simple_toggle(self, attr: str, activar: bool, crear_fn):
        plot = getattr(self, attr)
        if activar:
            if plot is None:
                setattr(self, attr, crear_fn())
            else:
                plot.show()
        else:
            if plot: plot.hide()

    # ── Helpers internos ────────────────────────────────

    def cambiar_titulo(self, symbol: str, interval: str):
        self.symbol = symbol
        self.interval = interval
        fplt.windows[0].setWindowTitle(f"{symbol}  ·  {interval}")

    @staticmethod
    def _ochl(df: pd.DataFrame) -> pd.DataFrame:
        return df[["Open", "Close", "High", "Low"]]

    def _dibujar_velas(self, df):
        self._plot_velas = fplt.candlestick_ochl(self._ochl(df), ax=self.ax_precio)

    def _dibujar_volumen(self, df):
        self._plot_vol = fplt.volume_ocv(df[["Open", "Close", "Volume"]], ax=self.ax_vol)