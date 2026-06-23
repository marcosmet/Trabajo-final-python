import pandas as pd
import numpy as np


# ──────────────────────────────────────────────
# EMA  —  Media Móvil Exponencial
# ──────────────────────────────────────────────

def ema(df: pd.DataFrame, periodo: int = 20) -> pd.Series:
    """
    Exponential Moving Average sobre el precio de cierre.

    Parámetros
    ----------
    df      : DataFrame con columna 'Close'
    periodo : número de velas para el cálculo (default 20)
    """
    return df["Close"].ewm(span=periodo, adjust=False).mean()


# ──────────────────────────────────────────────
# RSI  —  Relative Strength Index
# ──────────────────────────────────────────────

def rsi(df: pd.DataFrame, periodo: int = 14) -> pd.Series:
    """
    RSI clásico de Wilder (smoothed RS).

    Parámetros
    ----------
    df      : DataFrame con columna 'Close'
    periodo : ventana del RSI (default 14)
    """
    delta = df["Close"].diff()

    ganancia = delta.clip(lower=0)
    perdida = (-delta).clip(lower=0)

    avg_gan = ganancia.ewm(com=periodo - 1, min_periods=periodo).mean()
    avg_per = perdida.ewm(com=periodo - 1, min_periods=periodo).mean()

    rs = avg_gan / avg_per.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


# ──────────────────────────────────────────────
# VWAP  —  Volume Weighted Average Price
# ──────────────────────────────────────────────

def vwap(df: pd.DataFrame) -> pd.Series:
    """
    VWAP acumulado desde el inicio del DataFrame.
    Para uso intradiario, pasa solo las velas del día.

    Parámetros
    ----------
    df : DataFrame con columnas 'High', 'Low', 'Close', 'Volume'
    """
    precio_tipico = (df["High"] + df["Low"] + df["Close"]) / 3
    vol_acum = df["Volume"].cumsum()
    vwap_acum = (precio_tipico * df["Volume"]).cumsum() / vol_acum

    return vwap_acum


# ──────────────────────────────────────────────
# Bandas de Bollinger
# ──────────────────────────────────────────────

def bollinger(
        df: pd.DataFrame,
        periodo: int = 20,
        desviaciones: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bandas de Bollinger estándar.

    Devuelve
    --------
    (banda_media, banda_superior, banda_inferior)
    """
    media = df["Close"].rolling(window=periodo).mean()
    std = df["Close"].rolling(window=periodo).std()

    superior = media + desviaciones * std
    inferior = media - desviaciones * std

    return media, superior, inferior


# ──────────────────────────────────────────────
# MACD
# ──────────────────────────────────────────────

def macd(
        df: pd.DataFrame,
        rapida: int = 12,
        lenta: int = 26,
        señal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD clásico.

    Devuelve
    --------
    (linea_macd, linea_señal, histograma)
    """
    ema_rapida = df["Close"].ewm(span=rapida, adjust=False).mean()
    ema_lenta = df["Close"].ewm(span=lenta, adjust=False).mean()

    linea_macd = ema_rapida - ema_lenta
    linea_señal = linea_macd.ewm(span=señal, adjust=False).mean()
    histograma = linea_macd - linea_señal

    return linea_macd, linea_señal, histograma