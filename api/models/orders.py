from sqlalchemy import Column, DateTime, DECIMAL, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(DateTime, nullable=False, server_default=func.now())
    order_status = Column(String(50), nullable=False)
    order_type = Column(String(50), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    estimated_time = Column(Integer, nullable=False)

    promo_code = Column(String(50), ForeignKey("promo_codes.promo_code"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("restaurant_employees.employee_id"), nullable=True)

    payment = relationship("Payment", back_populates="order", uselist=False)
    promo = relationship("PromoCode", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("RestaurantEmployee", back_populates="orders")
    order_details = relationship("OrderDetails", back_populates="order", cascade="all, delete-orphan")