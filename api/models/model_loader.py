from . import (
    customer,
    employee,
    inventory,
    menu_item,
    menu_item_inventory,
    orders,
    payments,
    promo_codes,
    report,
    restaurant_manager,
    review,
    order_details
)
from ..dependencies.database import Base, engine


def index():
    Base.metadata.create_all(bind=engine)