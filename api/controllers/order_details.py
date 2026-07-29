from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import menu_item as menu_item_model
from ..models import order_details as model
from ..models import orders as order_model


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

    new_detail = model.OrderDetail(
        order_id=request.order_id,
        item_id=request.item_id,
        quantity=request.quantity,
        unit_price=request.unit_price,
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
        for field, value in update_data.items():
            setattr(detail, field, value)

        db.commit()
        db.refresh(detail)
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
        db.delete(detail)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)