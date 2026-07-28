from sqlalchemy import Column, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer,ForeignKey("orders.order_id", ondelete="CASCADE"),unique=True,nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="payment")