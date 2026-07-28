from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String(250), nullable=True)
    review_date = Column(Date, nullable=False, default=date.today)
    customer_id = Column(Integer,ForeignKey("customers.customer_id", ondelete="CASCADE"),nullable=False)
    item_id = Column(Integer,ForeignKey("menu_items.item_id", ondelete="CASCADE"),nullable=False)

    customer = relationship("Customer", back_populates="reviews")
    menu_item = relationship("MenuItem", back_populates="reviews")