from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import date, datetime, time
from decimal import Decimal

from ..models import orders as model
from ..models import promo_codes as promo_model


def validate_promo_code(db: Session, promo_code: str):
    code = (
        db.query(model.PromoCode)
        .filter(promo_model.PromoCode.promo_code == promo_code)
        .first()
    )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    if not code.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code is inactive"
        )

    if code.expiration_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code has expired"
        )

    return code


# Create
def create(db: Session, request):
    if request.promo_code:
        validate_promo_code(db=db, promo_code=request.promo_code)

    new_order = model.Order(
        order_status=request.order_status,
        order_type=request.order_type,
        total_price=Decimal("0.00"),
        estimated_time=request.estimated_time,
        promo_code=request.promo_code,
        customer_id=request.customer_id,
        employee_id=request.employee_id
    )

    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_order


# Read
def read_all(db: Session):
    try:
        return db.query(model.Order).order_by(model.Order.order_date.desc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, order_id: int):
    try:
        order = (
            db.query(model.Order)
            .filter(model.Order.order_id == order_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order


# Track Order
def track_order(db: Session, order_id: int):
    order = read_one(db=db, order_id=order_id)

    return {
        "order_id": order_id,
        "order_status": order.order_status,
        "order_type": order.order_type,
        "estimated_time": order.estimated_time
    }


# Read by Date Range
def read_by_date_range(db: Session, start_date: date, end_date: date):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    try:
        return db.query(model.Order).filter(
            model.Order.order_date >= start_datetime,
            model.Order.order_date <= end_datetime
        ).order_by(model.Order.order_date.asc()).all()

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


# Update
def update(db: Session, order_id: int, request):
    order = read_one(db=db, order_id=order_id)
    update_data = request.model_dump(exclude_unset=True)

    if "promo_code" in update_data and update_data["promo_code"]:
        validate_promo_code(db=db, promo_code=update_data["promo_code"])

    try:
        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return order


# Delete
def delete(db: Session, order_id: int):
    order = read_one(db=db, order_id=order_id)

    try:
        db.delete(order)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)