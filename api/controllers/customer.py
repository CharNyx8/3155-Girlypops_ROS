from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import customer as model


def create(db: Session, request):
    new_customer = model.Customer(
        name=request.name,
        email=request.email,
        phone=request.phone,
        has_account=request.has_account
    )

    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_customer


def read_all(db: Session):
    try:
        return db.query(model.Customer).order_by(model.Customer.name.asc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, customer_id: int):
    try:
        customer = (
            db.query(model.Customer)
            .filter(model.Customer.customer_id == customer_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


def update(db: Session, customer_id: int, request):
    customer = read_one(db=db, customer_id=customer_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return customer


def delete(db: Session, customer_id: int):
    customer = read_one(db=db, customer_id=customer_id)

    try:
        db.delete(customer)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)