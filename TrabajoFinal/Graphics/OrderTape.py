"""
OrderTape — Cinta de Órdenes a Mercado en Tiempo Real (Time & Sales)
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from datetime import datetime


class OrderTape(QWidget):
    def __init__(self):
        super().__init__()
        # Ventana flotante que siempre se queda arriba
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Live Market Tape")
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Consolas', monospace;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Título ─────────────────────────────────────────
        lbl_title = QLabel("▶ LIVE MARKET ORDERS")
        lbl_title.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        layout.addWidget(lbl_title)

        # ── Cabeceras de columnas ──────────────────────────
        header_layout = QHBoxLayout()
        for text in ["TIME", "PRICE", "AMOUNT"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #8b949e; font-size: 10px;")
            if text != "TIME":
                lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            header_layout.addWidget(lbl)
        layout.addLayout(header_layout)

        # ── Lista de órdenes ───────────────────────────────
        self.lista = QListWidget()
        self.lista.setStyleSheet("""
            QListWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #21262d;
            }
        """)
        self.lista.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Ocultar scrollbar por estética
        layout.addWidget(self.lista)

        self.max_items = 60  # Límite de órdenes en pantalla para no saturar memoria

    def agregar_orden(self, timestamp: int, precio: float, cantidad: float, es_venta: bool):
        """
        Agrega una nueva orden a la lista.
        es_venta = True (Taker Sell -> Magenta), False (Taker Buy -> Cyan)
        """
        # Formatear la hora
        dt = datetime.fromtimestamp(timestamp / 1000.0)
        hora_str = dt.strftime("%H:%M:%S")

        # Formatear textos
        precio_str = f"{precio:,.2f}"
        cant_str = f"{cantidad:,.4f}"

        # Color según el agresor del mercado
        color_texto = QColor("#ff00e5") if es_venta else QColor("#00e5ff")  # Magenta para Ventas, Cyan para Compras

        # Ensamblar la fila con formato de espaciado fijo
        fila_texto = f"{hora_str:<10} {precio_str:>10} {cant_str:>10}"

        item = QListWidgetItem(fila_texto)
        item.setForeground(color_texto)

        # Insertar siempre arriba (índice 0)
        self.lista.insertItem(0, item)

        # Eliminar el último si pasamos el límite
        if self.lista.count() > self.max_items:
            self.lista.takeItem(self.lista.count() - 1)