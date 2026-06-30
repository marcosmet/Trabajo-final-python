"""
ControlPanel  —  Ventana flotante de control (PyQt5).

Usa QWidget independiente en lugar de QDockWidget,
ya que finplot no expone un QMainWindow estándar.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont


# ─────────────────────────────────────────────────────────────
# Señales
# ─────────────────────────────────────────────────────────────

class Señales(QObject):
    cambiar_temporalidad = pyqtSignal(str, str)  # (symbol, interval)
    toggle_indicador     = pyqtSignal(str, bool)  # (nombre, activo)


# ─────────────────────────────────────────────────────────────
# Estilos dark
# ─────────────────────────────────────────────────────────────

STYLE_PANEL = """
    QWidget {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
    }
    QComboBox {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 4px 8px;
        min-height: 26px;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background-color: #161b22;
        color: #c9d1d9;
        selection-background-color: #1f6feb;
    }
    QPushButton {
        background-color: #1f6feb;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover   { background-color: #388bfd; }
    QPushButton:pressed { background-color: #1158c7; }
    QCheckBox {
        spacing: 8px;
        color: #c9d1d9;
        padding: 3px 0px;
    }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border: 1px solid #30363d;
        border-radius: 3px;
        background: #161b22;
    }
    QCheckBox::indicator:checked {
        background: #1f6feb;
        border-color: #1f6feb;
    }
"""

INTERVALOS = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]
SIMBOLOS   = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]


# ─────────────────────────────────────────────────────────────
# ControlPanel — ventana flotante independiente
# ─────────────────────────────────────────────────────────────

class ControlPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.señales = Señales()

        # Ventana flotante, siempre encima del gráfico
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Chart Control")
        self.setStyleSheet(STYLE_PANEL)
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(6)

        # ── Título ──────────────────────────────────────────
        self._lbl_titulo = QLabel("BTCUSDT")
        self._lbl_titulo.setStyleSheet(
            "color: #58a6ff; font-size: 14px; font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(self._lbl_titulo)

        self._separador(layout)

        # ── Símbolo ─────────────────────────────────────────
        layout.addWidget(self._lbl_sec("SÍMBOLO"))
        self._combo_simbolo = QComboBox()
        self._combo_simbolo.addItems(SIMBOLOS)
        layout.addWidget(self._combo_simbolo)

        # ── Temporalidad ────────────────────────────────────
        layout.addWidget(self._lbl_sec("TEMPORALIDAD"))
        self._combo_intervalo = QComboBox()
        self._combo_intervalo.addItems(INTERVALOS)
        layout.addWidget(self._combo_intervalo)

        # ── Botón Aplicar ────────────────────────────────────
        btn = QPushButton("▶  Aplicar")
        btn.clicked.connect(self._emitir_cambio)
        layout.addWidget(btn)

        self._separador(layout)

        # ── Indicadores ──────────────────────────────────────
        layout.addWidget(self._lbl_sec("INDICADORES"))

        self._checks = {}
        indicadores = [
            ("volumen",   "Volumen",          False),  # ◄ CORRECCIÓN: Arranca destildado
            ("ema20",     "EMA 20",           False),
            ("ema50",     "EMA 50",           False),
            ("bollinger", "Bollinger Bands",  False),
            ("vwap",      "VWAP",             False),
            ("rsi",       "RSI 14",           False),
            ("macd",      "MACD",             False),
            ("ordertape", "Order Tape (Live)", False),
        ]

        for nombre, etiqueta, inicial in indicadores:
            cb = QCheckBox(etiqueta)
            cb.setChecked(inicial)
            cb.stateChanged.connect(
                lambda estado, n=nombre: self.señales.toggle_indicador.emit(n, bool(estado))
            )
            self._checks[nombre] = cb
            layout.addWidget(cb)

        self._separador(layout)

        # ── Estado conexión ──────────────────────────────────
        self._lbl_estado = QLabel("● Conectado")
        self._lbl_estado.setStyleSheet("color: #3fb950; font-size: 11px;")
        layout.addWidget(self._lbl_estado)

        layout.addStretch()

    # ── Helpers de UI ────────────────────────────────────────

    @staticmethod
    def _separador(layout):
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("color: #21262d; margin: 4px 0px;")
        layout.addWidget(linea)

    @staticmethod
    def _lbl_sec(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "color: #8b949e; font-size: 10px; letter-spacing: 2px; margin-top: 4px;"
        )
        return lbl

    # ── Señales ──────────────────────────────────────────────

    def _emitir_cambio(self):
        simbolo   = self._combo_simbolo.currentText()
        intervalo = self._combo_intervalo.currentText()
        self._lbl_titulo.setText(simbolo)
        self.señales.cambiar_temporalidad.emit(simbolo, intervalo)

    # ── API pública ──────────────────────────────────────────

    def set_estado(self, texto: str, color: str = "#3fb950"):
        self._lbl_estado.setText(texto)
        self._lbl_estado.setStyleSheet(f"color: {color}; font-size: 11px;")

    def set_intervalo(self, intervalo: str):
        idx = self._combo_intervalo.findText(intervalo)
        if idx >= 0:
            self._combo_intervalo.setCurrentIndex(idx)