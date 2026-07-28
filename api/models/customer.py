from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    has_account = Column(Boolean, nullable=False, default=False)

    reviews = relationship("Review", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")