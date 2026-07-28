from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import inventory as model


def create(db: Session, request):
    new_item = model.Inventory(**request.model_dump())

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


def read_all(db: Session):
    try:
        return db.query(model.Inventory).order_by(model.Inventory.ingredient_name.asc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, ingredient_id: int):
    try:
        item = (
            db.query(model.Inventory)
            .filter(model.Inventory.ingredient_id == ingredient_id)
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
            detail=f"Inventory item with id {ingredient_id} not found"
        )

    return item


def update(db: Session, ingredient_id: int, request):
    item = read_one(db=db, ingredient_id=ingredient_id)
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


def delete(db: Session, ingredient_id: int):
    item = read_one(db=db, ingredient_id=ingredient_id)

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