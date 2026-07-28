from datetime import datetime

from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_name = Column(String(150), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    minimum_quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    maintained_by_manager_id = Column(Integer,ForeignKey("restaurant_managers.manager_id", ondelete="SET NULL"),nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    maintained_by = relationship("RestaurantManager", back_populates="inventory_items")
    menu_item_links = relationship("MenuItemInventory",back_populates="ingredient",cascade="all, delete-orphan")