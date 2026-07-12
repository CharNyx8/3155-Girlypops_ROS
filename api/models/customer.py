from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class Customer(Base):
    __tablename__ = 'customers'

    CustomerID = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    hasAccount = Column(Boolean, default=False)

    reviews = relationship("Review", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")
