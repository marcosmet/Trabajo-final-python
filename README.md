¡Bienvenido al motor de visualización en tiempo real de que desarrolle para mostrar lo aprendido con el lenguaje python Este módulo es una solución de gráficos financieros de alto rendimiento diseñada específicamente para el análisis cuantitativo y el procesamiento de datos de mercado de alta frecuencia (*High-Frequency Data Processing*). 

Con una estética institucional basada en una paleta *Cyberpunk/Neo-Minimalist*, la arquitectura separa de forma estricta el procesamiento matemático de los indicadores de la capa de renderizado visual, garantizando ejecuciones ultra fluidas sin bloqueos en la interfaz de usuario (*UI Freeze*).

---

## 🚀 Características Clave

* **Renderizado Asincrónico de Alta Velocidad:** Optimizado para recibir *ticks* en tiempo real desde WebSockets (ej. Binance API) sin degradación de frames.
* **Mecanismo Anti-Rebote (Smart Interaction Lock):** Implementación de detección por hardware a bajo nivel mediante hilos de Qt. Si el usuario arrastra el gráfico (*Panning*) o hace *Zoom* para analizar el pasado, el flujo en vivo se dibuja en segundo plano sin forzar saltos bruscos ni interrumpir la interacción.
* **Layout Dinámico Absoluto:** Sistema inteligente de colapso de paneles inferiores (Volumen, RSI, MACD) que recalculan el factor de estiramiento (*Row Stretch Factor*) de la grilla nativa en tiempo real para maximizar el área del gráfico principal.
* **Filtros de Color por Fuerza:** Los histogramas y volúmenes cambian su opacidad y tonalidad dinámicamente respondiendo a la presión compradora o vendedora.

---

## 🛠️ Arquitectura de Librerías (¿Por qué esta pila tecnológica?)

Para lograr un rendimiento apto para el trading institucional, se descartaron librerías tradicionales como *Matplotlib* (por su alto costo de CPU en rediseños completos) y se optó por un ecosistema basado en hardware dedicado:

### 1. Finplot (`finplot`)
Es el núcleo del renderizado de velas japonesas. Actúa como un *wrapper* especializado en finanzas sobre `pyqtgraph`. A diferencia de otras librerías, `finplot` optimiza los rangos de memoria utilizando estructuras de datos contiguas y solo redibuja los píxeles modificados en cada actualización de precio.

### 2. PyQtGraph (`pyqtgraph`)
Es el motor gráfico de bajo nivel. Utiliza el framework **QGraphicsView de Qt** e implementa optimizaciones matemáticas severas (como optimización de trazado de líneas analíticas). Se encarga de pintar el *Crosshair* (la cruz de seguimiento del mouse) y las etiquetas flotantes de coordenadas directamente mediante aceleración gráfica.

### 3. PyQt5 (`PyQt5`)
El framework industrial sobre el cual corre toda la aplicación. Proporciona la cola de eventos (*Event Loop*) principal, la gestión de hilos y el control preciso de los periféricos (detección de los botones del mouse mediante máscaras de bits).

### 4. Pandas (`pandas`)
La estructura de datos principal de la plataforma. El motor gráfico devora objetos `DataFrame` estructurados bajo el estándar `OHLCV` (Open, High, Low, Close, Volume) permitiendo rebanados de datos (*slicing*) en microsegundos.

---

📈 Indicadores Técnicos y Paneles Integrados

El motor procesa y renderiza tanto indicadores clásicos basados en la acción del precio como herramientas analíticas de nivel institucional:

Live Market Tape (Cinta de Órdenes - Taker Trades): Panel flotante independiente de alta velocidad (Time & Sales) que captura cada orden ejecutada a mercado a nivel global. Utiliza colores nemotécnicos (CYAN para compras institucionales agresivas / Taker Buys y MAGENTA para ventas agresivas / Taker Sells). Representa la transición del trading tradicional hacia el análisis de datos tangibles en tiempo real.

Volumen Transaccional: Panel inferior independiente que muestra la cantidad de operaciones, suavizado con transparencias para no saturar la vista del operador.

EMA (Exponential Moving Average): Medias móviles configuradas en 20 y 50 períodos para detección micro/macro de tendencias directamente sobre el precio.

Bollinger Bands (BB): Cálculo de volatilidad estadística mediante desviaciones estándar aplicadas sobre una media móvil.

VWAP (Volume-Weighted Average Price): Indicador de referencia institucional indispensable que calcula el precio promedio ponderado por volumen para identificar el precio justo intradiario.

RSI & MACD: Osciladores de momentum e histogramas de fuerza integrados para confirmaciones analíticas tradicionales.

---

## 📂 Estructura del Proyecto

La arquitectura del sistema sigue un patrón modular limpio, desacoplando de manera estricta la conexión con el bróker, el manejo de estructuras de datos en memoria, la lógica matemática de los indicadores y los componentes visuales de la interfaz de usuario:

```text
├── main.py                     # Punto de entrada principal del motor gráfico.
├── requirements.txt            # Archivo de dependencias del entorno de Python.
├── Binance/
│   ├── BinanceRest.py          # Cliente API REST para descargas históricas de datos.
│   └── BinanceWebSocket.py     # Conexión persistente y gestión de streams combinados (Velas + Trades).
├── Data/
│   └── KlineManager.py         # Gestor de memoria y formateo dinámico de DataFrames de Pandas.
├── Graphics/
│   ├── CandleChart.py          # Renderizador de gráficos financieros con Finplot.
│   ├── ControlPanel.py         # Ventana flotante de controles y toggles de indicadores en PyQt5.
│   └── OrderTape.py            # Componente de cinta de órdenes en tiempo real (Order Flow).
├── Indicadores/
│   └── indicadores.py          # Librería matemática pura para cálculos cuantitativos.
└── Models/
    └── Vela.py                 # Clase de datos de tipo entidad (Model) para tipado estricto de velas.


⚙️ Optimización de UI y Concurrencia Destacada
Uno de los mayores desafíos de ingeniería fue el control de flujos concurrentes. Los datos del WebSocket se reciben en un hilo secundario y se inyectan a la interfaz gráfica mediante señales Qt estrictamente seguras (pyqtSignal), evitando corrupciones de memoria y congelamientos de UI:

def _on_trade_gui(self, trade_data: dict):
    """ Dibuja el trade en la UI solo si el panel está visible """
    if self.tape and self.tape.isVisible():
        self.tape.agregar_orden(
            timestamp=trade_data["T"],
            precio=float(trade_data["p"]),
            cantidad=float(trade_data["q"]),
            es_venta=trade_data["m"] # m=True indica Taker Sell (Venta Agresiva)
        )

Además, el sistema cuenta con optimización pasiva: si la ventana de la cinta de órdenes está oculta, el software descarta visualmente los datos para ahorrar ciclos de CPU, activando el renderizado ultra-rápido solo cuando el operador decide tildar la herramienta.

🔧 Instalación y Requisitos
Requisitos Previos
Python 3.10 o superior instalado en el sistema.

Administrador de paquetes de Python (pip) actualizado.

Paso 1: Instalación de Dependencias
Para configurar el entorno con todas las librerías necesarias para el procesamiento de gráficos, la interfaz de usuario y la conexión de alta frecuencia a la API de Binance, ejecutá el siguiente comando en tu terminal:

Bash
```text
pip install pandas finplot PyQt5 pyqtgraph websocket-client

Paso 2: Lanzar la Aplicación
Una vez completada la instalación de los paquetes, iniciá el motor principal ejecutando:

Bash
```text
python main.py

(Opcional) Podés pasar argumentos por consola para iniciar un par o temporalidad específica por defecto:

Bash
```text
python main.py --symbol ETHUSDT --interval 5m





