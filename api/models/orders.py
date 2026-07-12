from sqlalchemy import Column, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    orderID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    orderDate = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    orderStatus = Column(String(50), nullable=False)
    orderType = Column(String(50), nullable=False)
    totalPrice = Column(DECIMAL(10, 2), nullable=False)
    estimatedTime = Column(Integer, nullable=False)

    order_details = relationship("OrderDetail", back_populates="order")