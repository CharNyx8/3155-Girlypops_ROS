from _pytest import reports

from . import orders, inventory, menu_item, menu_item_inventory
from . import employee
from . import reviews
from . import restaurant_manager
from . import report

def load_routes(app):
    app.include_router(orders.router)
    app.include_router(reviews.router)
    app.include_router(employee.router)
    app.include_router(restaurant_manager.router)
    app.include_router(report.router)
    app.include_router(inventory.router)
    app.include_router(menu_item.router)
    app.include_router(menu_item_inventory.router)

