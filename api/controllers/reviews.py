from urllib import request

from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import customer
from ..models import customer as customer_model
from ..models import menu_item as menu_item_model
from ..models import review as model

def create(db: Session, request):
    customer = (
        db.query(customer_model.Customer)
        .filter(customer_model.Customer.customerID == request.customerID)
        .first()
    )

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    menu_item = (
        db.query(menu_item_model.MenuItem)
        .filter(menu_item_model.MenuItem.itemID == request.item_i)
        .first()
    )

    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MenuItem not found")

    new_review = model.Review(
        rating = request.rating,
        customerID = request.customerID,
        item_id = request.item_id,
        comment = request.comment
    )

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(error.__dict__.get("orig", error))
        )

    return new_review

def read_all(db: Session):
    try:
        return(
            db.query(model.Review)
            .order_by(model.Review.reviewDate.desc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(error.__dict__.get("orig", error))
        )

def read_one (db: session, review_id: int):
    review = (
        db.query(model.Review)
        .filter(model.Review.reviewID == review_id)
        .first()
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
        .filter(
            menu_item_model.MenuItem.itemID == item_id
        )
        .first()
    )

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MenuItem not found"
        )

    try:
        return(
            db.query(model.Review)
            .filter(model.Review.item_id == item_id)
            .order_by(model.Review.reviewDate.desc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(error.__dict__.get("orig", error))
        )

def update(db: Session, review_id: int, request):
    review_query = (
        db.query(model.Review)
        .filter(model.Review.reviewID == review_id)
    )
    review = review_query.first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    try:
        update_data = request.model_dump(
            exclude_unset=True
        )

        review_query.update(
            update_data,
            synchronize_session=False
        )
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = str(error.__dict__.get("orig", error))
        )
    return review_query.first()

##Still Need to add a Delete Function