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

## 📈 Indicadores Técnicos Integrados

El motor cuenta con un archivo analítico modular (`Indicators/indicadores.py`) que procesa matemáticamente los siguientes algoritmos de mercado:

* **EMA (Exponential Moving Average):** Configurada por defecto en períodos de 20 y 50 para la detección de tendencias micro y macro.
* **Bollinger Bands (BB):** Cálculo de volatilidad estadística mediante desviaciones estándar aplicadas sobre una media móvil, ideal para detectar sobrecompra o canales de compresión (*Squeezes*).
* **VWAP (Volume-Weighted Average Price):** Indicador de referencia institucional que calcula el precio promedio ponderado por volumen, clave para identificar el precio justo (*Fair Value*) intradiario.
* **RSI (Relative Strength Index):** Oscilador de momentum de 14 períodos para identificar la velocidad y el cambio de los movimientos de precios.
* **MACD (Moving Average Convergence Divergence):** Sistema de cruce de medias con histograma de fuerza integrado para la confirmación de señales de entrada y salida.
* **Volumen Transaccional:** Panel inferior independiente que muestra la cantidad de operaciones. Utiliza transparencias personalizadas (`CYAN_VOL` y `MAGENTA_VOL`) para integrarse de forma limpia con el fondo oscuro sin saturar la vista.

---

## 📂 Estructura del Módulo

```text
├── main.py                     # Punto de entrada principal de la aplicación.
├── Graphics/
│   └── CandleChart.py          # Motor visual, control de Layouts y temas gráficos.
└── Indicators/
    └── indicadores.py          # Funciones matemáticas puras (Cálculo cuantitativo).
