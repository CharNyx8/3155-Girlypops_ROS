from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional

from ..models import menu_item as model


# Create
def create(db: Session, request):
    new_item = model.MenuItem(**request.model_dump())

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_item


# Read
def read_all(db: Session):
    try:
        return db.query(model.MenuItem).order_by(model.MenuItem.item_name.asc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, item_id: int):
    try:
        item = (
            db.query(model.MenuItem)
            .filter(model.MenuItem.item_id == item_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {item_id} not found"
        )

    return item


# Search
def search(
    db: Session,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    dietary_type: Optional[str] = None,
    available_only: bool = True
):
    try:
        query = db.query(model.MenuItem)

        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                model.MenuItem.item_name.ilike(search_term)
                | model.MenuItem.description.ilike(search_term)
            )

        if category:
            query = query.filter(
                model.MenuItem.category.ilike(category)
            )

        if dietary_type:
            query = query.filter(
                model.MenuItem.dietary_type.ilike(dietary_type)
            )

        if available_only:
            query = query.filter(
                model.MenuItem.is_available.is_(True)
            )

        return query.order_by(
            model.MenuItem.item_name.asc()
        ).all()

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


# Update
def update(db: Session, item_id: int, request):
    item = read_one(db=db, item_id=item_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(item, field, value)

        db.commit()
        db.refresh(item)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return item


# Delete
def delete(db: Session, item_id: int):
    item = read_one(db=db, item_id=item_id)

    try:
        db.delete(item)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)