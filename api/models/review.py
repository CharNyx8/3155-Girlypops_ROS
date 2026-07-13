from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from ..dependencies.database import Base

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key = True, autoincrement = True)
    comment = Column(String(250), nullable = True)
    rating = Column(Integer, nullable = False)
    review_date = Column(Date, default = date.today)

    customer_id = Column(Integer, ForeignKey('customers.customer_id', ondelete = "CASCADE"), nullable = False)

    customer = relationship("Customer", back_populates = "reviews")