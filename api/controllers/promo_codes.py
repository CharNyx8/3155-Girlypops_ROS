from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import promo_codes as model


# Create
def create(db: Session, request):
    new_promo_code = model.PromoCode(
        promo_code=request.promo_code,
        discount_amount=request.discount_amount,
        expiration_date=request.expiration_date,
        is_active=request.is_active,
        manager_id=request.manager_id
    )

    try:
        db.add(new_promo_code)
        db.commit()
        db.refresh(new_promo_code)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_promo_code


# Read
def read_all(db: Session):
    try:
        return db.query(model.PromoCode).order_by(model.PromoCode.promo_code.asc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, promo_code: str):
    try:
        code = (
            db.query(model.PromoCode)
            .filter(model.PromoCode.promo_code == promo_code)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    return code


# Update
def update(db: Session, promo_code: str, request):
    code = read_one(db=db, promo_code=promo_code)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(code, field, value)

        db.commit()
        db.refresh(code)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return code


# Delete
def delete(db: Session, promo_code: str):
    code = read_one(db=db, promo_code=promo_code)

    try:
        db.delete(code)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)