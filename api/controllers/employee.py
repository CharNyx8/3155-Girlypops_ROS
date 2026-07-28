from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import employee as model

def create(db: Session, request):

    new_employee = model.RestaurantEmployee(
        employee_id = request.employee_id,
        name = request.name,
        role = request.role,
    )

    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )
    return new_employee

def read_all(db:Session):
    try:
        employees =(
            db.query(model.RestaurantEmployee)
            .order_by(model.restaurantEmployee.name.asc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )
    return employees

def read_one(db:Session, employee_id: int):
    employee =(
        db.query(model.RestaurantEmployee)
        .filter(model.RestaurantEmployee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

def update(db: Session, employee_id: int, request):
    employee_query = (
        db.query(model.RestaurantEmployee)
        .filter(model.RestaurantEmployee.id == employee_id)
    )

    employee = employee_query.first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    try:
        update_data = request.model_dump(exclude_unset=True)

        employee_query.update(
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

    return employee_query.first()

def delete(db: Session, employee_id: int):
    employee_query = (
        db.query(model.RestaurantEmployee)
        .filter(model.RestaurantEmployee.id == employee_id)
    )

    employee = employee_query.first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    try:
        employee_query.delete(
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
