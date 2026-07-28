from fastapi import HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import report as model
from ..models import restaurant_manager as manager_model


def find_manager(db: Session, manager_id: int):
    manager = (
        db.query(manager_model.RestaurantManager)
        .filter(manager_model.RestaurantManager.manager_id == manager_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant manager not found"
        )

    return manager


def create(db: Session, request):
    if request.generated_by_manager_id is not None:
        find_manager(db=db, manager_id=request.generated_by_manager_id)

    new_report = model.Report(
        report_name=request.report_name,
        generated_by_manager_id=request.generated_by_manager_id
    )

    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return new_report


def read_all(db: Session):
    try:
        return db.query(model.Report).order_by(model.Report.date_generated.desc()).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )


def read_one(db: Session, report_id: int):
    try:
        report = (
            db.query(model.Report)
            .filter(model.Report.report_id == report_id)
            .first()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return report


def update(db: Session, report_id: int, request):
    report = read_one(db=db, report_id=report_id)
    update_data = request.model_dump(exclude_unset=True)

    if "generated_by_manager_id" in update_data:
        manager_id = update_data["generated_by_manager_id"]
        if manager_id is not None:
            find_manager(db=db, manager_id=manager_id)

    try:
        for field, value in update_data.items():
            setattr(report, field, value)

        db.commit()
        db.refresh(report)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return report


def delete(db: Session, report_id: int):
    report = read_one(db=db, report_id=report_id)

    try:
        db.delete(report)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)