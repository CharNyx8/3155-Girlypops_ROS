from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import date, datetime, time

from ..models import orders as model


# Create
def create(db: Session, request):
    new_order = model.Order(
        order_status=request.order_status,
        order_type=request.order_type,
        total_price=request.total_price,
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