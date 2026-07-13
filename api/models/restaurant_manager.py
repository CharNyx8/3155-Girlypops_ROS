from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class RestaurantManager(Base):
    __tablename__ = "restaurant_managers"

    manager_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), index=True, nullable=False)

    menu_items = relationship("MenuItem", back_populates="created_by", cascade="all, delete-orphan")
    inventory_items = relationship("Inventory", back_populates="maintained_by", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="generated_by", cascade="all, delete-orphan")
    promoCodes = relationship("PromoCode", back_populates="manager")