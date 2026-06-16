from dataclasses import dataclass
from datetime import datetime


@dataclass
class Kline:
    open_time: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float
