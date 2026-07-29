from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import restaurant_manager as model


# Create
def create(db: Session, request):
    new_manager = model.RestaurantManager(
        name=request.name,
        email=request.email
    )

    try:
        db.add(new_manager)
        db.commit()
        db.refresh(new_manager)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_manager


# Read
def read_all(db: Session):
    try:
        return (
            db.query(model.RestaurantManager)
            .order_by(model.RestaurantManager.name.asc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, manager_id: int):
    try:
        manager = (
            db.query(model.RestaurantManager)
            .filter(model.RestaurantManager.manager_id == manager_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    return manager


# Update
def update(db: Session, manager_id: int, request):
    manager = read_one(db=db, manager_id=manager_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(manager, field, value)

        db.commit()
        db.refresh(manager)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return manager


# Delete
def delete(db: Session, manager_id: int):
    manager = read_one(db=db, manager_id=manager_id)

    try:
        db.delete(manager)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)