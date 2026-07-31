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
    reviews,
    order_details
)


def load_routes(app):
    app.include_router(customer.router)
    app.include_router(employee.router)
    app.include_router(inventory.router)
    app.include_router(menu_item.router)
    app.include_router(menu_item_inventory.router)
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(payments.router)
    app.include_router(promo_codes.router)
    app.include_router(report.router)
    app.include_router(restaurant_manager.router)
    app.include_router(reviews.router)