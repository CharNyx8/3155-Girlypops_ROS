from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import menu_item_inventory as model


def create(db: Session, request):
    new_link = model.MenuItemInventory(**request.model_dump())

    try:
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_link


def read_all(db: Session):
    try:
        return db.query(model.MenuItemInventory).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, item_id: int, ingredient_id: int):
    try:
        link = (
            db.query(model.MenuItemInventory)
            .filter(
                model.MenuItemInventory.item_id == item_id,
                model.MenuItemInventory.ingredient_id == ingredient_id
            )
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link between menu item {item_id} and ingredient {ingredient_id} not found"
        )

    return link


def update(db: Session, item_id: int, ingredient_id: int, request):
    link = read_one(db=db, item_id=item_id, ingredient_id=ingredient_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(link, field, value)

        db.commit()
        db.refresh(link)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return link


def delete(db: Session, item_id: int, ingredient_id: int):
    link = read_one(db=db, item_id=item_id, ingredient_id=ingredient_id)

    try:
        db.delete(link)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)