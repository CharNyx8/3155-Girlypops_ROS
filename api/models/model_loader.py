from _pytest import reports

from . import orders, order_details, recipes, menu_item, inventory, menu_item_inventory, report, restaurant_manager

from ..dependencies.database import engine


def index():
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    inventory.Base.metadata.create_all(engine)
    menu_item.Base.metadata.create_all(engine)
    menu_item_inventory.Base.metadata.create_all(engine)
    report.Base.metadata.create_all(engine)
    restaurant_manager.Base.metadata.create_all(engine)
