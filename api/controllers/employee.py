from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import employee as model


def create(db: Session, request):
    new_employee = model.RestaurantEmployee(
        name=request.name,
        role=request.role
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


def read_all(db: Session):
    try:
        return (
            db.query(model.RestaurantEmployee)
            .order_by(model.RestaurantEmployee.name.asc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, employee_id: int):
    try:
        employee = (
            db.query(model.RestaurantEmployee)
            .filter(model.RestaurantEmployee.employee_id == employee_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


def update(db: Session, employee_id: int, request):
    employee = read_one(db=db, employee_id=employee_id)
    update_data = request.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(employee, field, value)

        db.commit()
        db.refresh(employee)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return employee


def delete(db: Session, employee_id: int):
    employee = read_one(db=db, employee_id=employee_id)

    try:
        db.delete(employee)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)