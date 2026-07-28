from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    report_name = Column(String(150), nullable=False)
    date_generated = Column(DateTime, nullable=False, default=datetime.now)
    generated_by_manager_id = Column(Integer,ForeignKey("restaurant_managers.manager_id", ondelete="SET NULL"),nullable=True)

    generated_by = relationship("RestaurantManager", back_populates="reports")