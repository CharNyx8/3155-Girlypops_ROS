from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    paymentID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    orderID = Column(Integer, ForeignKey("orders.orderID"), unique=True, nullable=False)
    paymentMethod = Column(String(50), nullable=False)
    paymentStatus = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="payment")
