from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class RestaurantEmployee(Base):
    __tablename__ = "restaurant_employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)

    orders = relationship("Order", back_populates="employee")