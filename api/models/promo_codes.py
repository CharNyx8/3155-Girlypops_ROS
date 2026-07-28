from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    promo_code = Column(String(50), primary_key=True)
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    manager_id = Column(Integer,ForeignKey("restaurant_managers.manager_id", ondelete="CASCADE"), nullable=False)

    orders = relationship("Order", back_populates="promo")
    manager = relationship("RestaurantManager", back_populates="promo_codes")