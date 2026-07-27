from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import restaurant_manager as model

def create(db: Session, Request):
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
            detail=str(error.__dict__.get("orig",error))
        )
    return new_manager

def read_all(db: Session):
    try:
        managers = (
            db.query(model.RestaurantManager)
            .order_by(model.RestaurantManager.name.asc())
            .all()
        )

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return managers

def read_one(db: Session, manager_id: int):
    manager = (
        db.query(model.RestaurantManager)
        .filter(model.RestaurantManager.manager_id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    return manager

def update(db: Session, manager_id: int, request):
    manager_query = (
        db.query(model.RestaurantManager)
        .filter(
            model.RestaurantManager.manager_id == manager_id
        )
    )

    manager = manager_query.first()

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    try:
        update_data = request.model_dump(
            exclude_unset=True
        )

        manager_query.update(
            update_data,
            synchronize_session=False
        )

        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return manager_query.first()

def delete(db: Session, manager_id: int):
    manager_query = (
        db.query(model.RestaurantManager)
        .filter(
            model.RestaurantManager.manager_id == manager_id
        )
    )

    manager = manager_query.first()

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    try:
        manager_query.delete(
            synchronize_session=False
        )

        db.commit()

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

