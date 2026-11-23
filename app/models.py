from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from .database import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    sku = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, default="General")
    quantity = Column(Float, nullable=False, default=0)
    minimum_stock = Column(Float, nullable=False, default=0)
    unit_cost = Column(Float, nullable=False, default=0)
    supplier = Column(String(200), nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

