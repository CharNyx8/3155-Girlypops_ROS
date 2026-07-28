from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import customer as customer_model
from ..models import menu_item as menu_item_model
from ..models import review as model


def create(db: Session, request):
    customer = (
        db.query(customer_model.Customer)
        .filter(customer_model.Customer.customer_id == request.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
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

    new_review = model.Review(
        rating=request.rating,
        comment=request.comment,
        customer_id=request.customer_id,
        item_id=request.item_id
    )

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_review


def read_all(db: Session):
    try:
        return db.query(model.Review).order_by(model.Review.review_date.desc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, review_id: int):
    try:
        review = (
            db.query(model.Review)
            .filter(model.Review.review_id == review_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    return review


def read_by_menu_item(db: Session, item_id: int):
    menu_item = (
        db.query(menu_item_model.MenuItem)
        .filter(menu_item_model.MenuItem.item_id == item_id)
        .first()
    )

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    try:
        return (
            db.query(model.Review)
            .filter(model.Review.item_id == item_id)
            .order_by(model.Review.review_date.desc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def update(db: Session, review_id: int, request):
    review = read_one(db=db, review_id=review_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(review, field, value)

        db.commit()
        db.refresh(review)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return review


def delete(db: Session, review_id: int):
    review = read_one(db=db, review_id=review_id)

    try:
        db.delete(review)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)