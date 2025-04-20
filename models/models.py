from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    id: int
    name: str
    code: str
    category: str
    unit: str
    price: float
    description: str
    threshold: int
    created_at: datetime

@dataclass
class StockMovement:
    id: int
    product_id: int
    type: str
    label: str
    reason: str
    service: str
    quantity: int
    timestamp: datetime
