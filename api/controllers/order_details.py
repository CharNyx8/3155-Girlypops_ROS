from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from decimal import Decimal

from ..models import menu_item as menu_item_model
from ..models import order_details as model
from ..models import orders as order_model
from ..models import inventory as inventory_model
from ..models import menu_item_inventory as menu_item_inventory_model


def get_inventory_requirements(db: Session, item_id: int):
    try:
        return (
            db.query(menu_item_inventory_model.MenuItemInventory)
            .filter(menu_item_inventory_model.MenuItemInventory.item_id == item_id)
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def adjust_inventory(db: Session, item_id: int, quantity_change: int):
    requirements = get_inventory_requirements(
        db=db,
        item_id=item_id
    )

    inventory_adjustments = []
    shortages = []

    for requirement in requirements:
        ingredient = (
            db.query(inventory_model.Inventory)
            .filter(
                inventory_model.Inventory.ingredient_id
                == requirement.ingredient_id
            )
            .first()
        )

        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Inventory ingredient "
                    f"{requirement.ingredient_id} not found"
                )
            )

        required_amount = (Decimal(requirement.quantity_required) * Decimal(quantity_change))

        new_quantity = (Decimal(ingredient.quantity) - required_amount)

        if new_quantity < 0:
            shortages.append({
                "ingredient_id": ingredient.ingredient_id,
                "ingredient_name": ingredient.ingredient_name,
                "required": required_amount,
                "available": ingredient.quantity
            })

        inventory_adjustments.append((ingredient, new_quantity))

    if shortages:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Insufficient ingredients",
                "shortages": shortages
            }
        )

    for ingredient, new_quantity in inventory_adjustments:
        ingredient.quantity = new_quantity


# Create
def create(db: Session, request):
    order = (
        db.query(order_model.Order)
        .filter(order_model.Order.order_id == request.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    menu_item = (
        db.query(menu_item_model.MenuItem)
        .filter(menu_item_model.MenuItem.item_id == request.item_id)
        .first()
    )

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    adjust_inventory(
        db=db,
        item_id=request.item_id,
        quantity_change=request.quantity
    )

    new_detail = model.OrderDetail(
        order_id=request.order_id,
        item_id=request.item_id,
        quantity=request.quantity,
        unit_price=menu_item.price,
        special_instructions=request.special_instructions
    )

    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_detail


# Read
def read_all(db: Session):
    try:
        return db.query(model.OrderDetail).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, order_detail_id: int):
    try:
        detail = (
            db.query(model.OrderDetail)
            .filter(model.OrderDetail.order_detail_id == order_detail_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order detail not found"
        )

    return detail


# Read by Order
def read_by_order(db: Session, order_id: int):
    order = (
        db.query(order_model.Order)
        .filter(order_model.Order.order_id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    try:
        return (
            db.query(model.OrderDetail)
            .filter(model.OrderDetail.order_id == order_id)
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


# Update
def update(db: Session, order_detail_id: int, request):
    detail = read_one(db=db, order_detail_id=order_detail_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        if "quantity" in update_data:
            new_quantity = update_data["quantity"]
            quantity_change = (new_quantity - detail.quantity)

            if quantity_change != 0:
                adjust_inventory(db=db, item_id=detail.item_id, quantity_change=quantity_change)

        for field, value in update_data.items():
            setattr(detail, field, value)

        db.commit()
        db.refresh(detail)

    except HTTPException:
            db.rollback()
            raise

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return detail


# Delete
def delete(db: Session, order_detail_id: int):
    detail = read_one(db=db, order_detail_id=order_detail_id)

    try:
        adjust_inventory(db=db, item_id=detail.item_id, quantity_change=-detail.quantity)

        db.delete(detail)
        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)