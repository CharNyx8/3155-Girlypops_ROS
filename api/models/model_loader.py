from _pytest import reports

from . import orders, order_details, recipes, menu_item, inventory, menu_item_inventory, report, restaurant_manager
from . import orders, order_details, recipes, sandwiches, resources, payments, promo_codes

from ..dependencies.database import engine
from .employee import RestaurantEmployee


def index():
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    inventory.Base.metadata.create_all(engine)
    menu_item.Base.metadata.create_all(engine)
    menu_item_inventory.Base.metadata.create_all(engine)
    report.Base.metadata.create_all(engine)
    restaurant_manager.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
    payments.Base.metadata.create_all(engine)
    promo_codes.Base.metadata.create_all(engine)
