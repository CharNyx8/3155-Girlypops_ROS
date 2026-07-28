from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class RestaurantEmployee(Base):
    __tablename__ = "restaurant_employees"

    id = Column(Integer, primary_key=True, index=True)

    employeeID = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)

    orders = relationship("Order", back_populates="employee")