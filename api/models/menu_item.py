from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(100), nullable=True)
    dietary_type = Column(String(50), nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)
    created_by_manager_id = Column(Integer,ForeignKey("restaurant_managers.manager_id", ondelete="SET NULL"),nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    created_by = relationship("RestaurantManager", back_populates="menu_items")
    ingredient_links = relationship("MenuItemInventory",back_populates="menu_item",cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="menu_item", cascade="all, delete-orphan")
    order_details = relationship("OrderDetails", back_populates="menu_item", cascade="all, delete-orphan")