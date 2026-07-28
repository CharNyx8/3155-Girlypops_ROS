from fastapi import HTTPException, Response, status
from pygments.lexers import q
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import report as model
from ..models import restaurant_manager as manager_model

def create(db: Session, request):
    if request.generated_by_manager_id is not None:
        manager = (
            db.query(manager_model.RestaurantManager)
            .filter(
                manager_model.RestaurantManager.manager_id
                == request.generated_by_manager_id
            )
            .first()
        )

        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant manager not found"
            )

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
        reports = (
            db.query(model.Report)
            .order_by(model.Report.date_generated.desc())
            .all()
        )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )
    return reports

def read_one(db: Session, id: int):
    report = (
        db.query(model.Report)
        .filter(model.Report.report_id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return report

def update(db: Session, report_id: int, request):
    report_query = (
        db.query(model.Report)
        .filter(model.Report.report_id == report_id)
    )

    report = report_query.first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    try:
        update_data = request.model_dump(
            exclude_unset=True
        )

        report_query.update(
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
    return report_query.first()

def delete(db: Session, report_id: int):
    report_query = (
        db.query(model.Report)
        .filter(model.Report.report_id == report_id)
    )

    report = report_query.first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    try:
        report_query.delete(
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



