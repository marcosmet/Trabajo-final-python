import pandas as pd


class KlineManager:
    """
    Almacena y gestiona las velas de una temporalidad.
    Mantiene el histórico y actualiza la vela en curso via WebSocket.
    """

    def __init__(self, max_velas=1000):
        self.klines = []
        self.max_velas = max_velas

    # ------------------------------------------------------------------
    # Carga y actualización
    # ------------------------------------------------------------------

    def cargar_historico(self, klines):
        self.klines = list(klines[-self.max_velas:])

    def actualizar(self, nueva_kline):
        """
        Si la vela tiene el mismo open_time que la última, la reemplaza
        (actualización en vivo). Si no, la agrega como vela nueva.
        """
        if not self.klines:
            self.klines.append(nueva_kline)
            return

        ultima = self.klines[-1]

        if ultima.open_time == nueva_kline.open_time:
            self.klines[-1] = nueva_kline
        else:
            self.klines.append(nueva_kline)
            # Limitar memoria
            if len(self.klines) > self.max_velas:
                self.klines = self.klines[-self.max_velas:]

    # ------------------------------------------------------------------
    # Acceso
    # ------------------------------------------------------------------

    def obtener_todas(self):
        return self.klines

    def ultima(self):
        return self.klines[-1] if self.klines else None

    # ------------------------------------------------------------------
    # DataFrames
    # ------------------------------------------------------------------

    def dataframe(self):
        return self._construir_df(self.klines)

    def dataframe_ultimas(self, cantidad=500):
        return self._construir_df(self.klines[-cantidad:])

    def _construir_df(self, klines):
        if not klines:
            return pd.DataFrame(
                columns=["Open", "High", "Low", "Close", "Volume"]
            )

        data = [
            {
                "Open": k.open,
                "High": k.high,
                "Low": k.low,
                "Close": k.close,
                "Volume": k.volume,
            }
            for k in klines
        ]

        return pd.DataFrame(
            data,
            index=[k.open_time for k in klines]
        )