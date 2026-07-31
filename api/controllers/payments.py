from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import payments as model
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

    existing_payment = (
        db.query(model.Payment)
        .filter(model.Payment.order_id == request.order_id)
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment already exists"
        )

    if order.total_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total must be greater than 0"
        )


    new_payment = model.Payment(
        order_id=request.order_id,
        payment_method=request.payment_method,
        payment_status=r"Paid",
        amount=order.total_price
    )

    try:
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_payment


# Read
def read_all(db: Session):
    try:
        return db.query(model.Payment).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, payment_id: int):
    try:
        payment = (
            db.query(model.Payment)
            .filter(model.Payment.payment_id == payment_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


# Update
def update(db: Session, payment_id: int, request):
    payment = read_one(db=db, payment_id=payment_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(payment, field, value)

        db.commit()
        db.refresh(payment)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return payment


# Delete
def delete(db: Session, payment_id: int):
    payment = read_one(db=db, payment_id=payment_id)

    try:
        db.delete(payment)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)