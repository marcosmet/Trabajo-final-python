import pandas as pd


class KlineManager:

    def __init__(self):

        self.klines = []

    def cargar_historico(self, klines):

        self.klines = klines

    def obtener_todas(self):

        return self.klines

    def ultima(self):

        if not self.klines:
            return None

        return self.klines[-1]

    def actualizar(self, nueva_kline):

        if not self.klines:

            self.klines.append(nueva_kline)
            return

        ultima = self.klines[-1]

        if ultima.open_time == nueva_kline.open_time:

            self.klines[-1] = nueva_kline

        else:

            self.klines.append(nueva_kline)

    def dataframe(self):

        data = []

        for k in self.klines:

            data.append({
                "Open": k.open,
                "High": k.high,
                "Low": k.low,
                "Close": k.close,
                "Volume": k.volume
            })

        df = pd.DataFrame(
            data,
            index=[k.open_time for k in self.klines]
        )

        return df

    def dataframe_ultimas(self, cantidad=500):

        data = []

        klines = self.klines[-cantidad:]

        for k in klines:

            data.append({
                "Open": k.open,
                "High": k.high,
                "Low": k.low,
                "Close": k.close,
                "Volume": k.volume
            })

        return pd.DataFrame(
            data,
            index=[k.open_time for k in klines]
        )