from . import orders, order_details
from . import employee
from . import reviews
from .import restaurant_manager

def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(reviews.router)
    app.include_router(employee.router)
    app.include_router(restaurant_manager.router)


