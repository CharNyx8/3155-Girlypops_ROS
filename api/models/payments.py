from sqlalchemy import Column, Integer, String, DECIMAL
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    paymentID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paymentMethod = Column(String(50), nullable=False)
    paymentStatus = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
