from fastapi import HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import date, datetime, time
from decimal import Decimal

from ..models import report as model
from ..models import restaurant_manager as manager_model
from ..models import orders as order_model
from ..models import paymentgs as payment_model


# Find Manager
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


# Create
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


# Read
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


# Daily Revenue
def read_daily_revenue(db: Session, report_date: date):
    start_datetime = datetime.combine(report_date, time.min)
    end_datetime = datetime.combine(report_date, time.max)

    try:
        result = (
            db.query(func.count(payment_model.Payment.payment_id),
                     func.coalesce(func.sum(payment_model.Payment.amount), 0)
        ).join(
                order_model.Order,
                payment_model.Payment.order_id == order_model.Order.order_id
        ).filter(
                order_model.Order.order_date >= start_datetime,
                order_model.Order.order_date <= end_datetime,
                payment_model.Payment.payment_status == "Paid"
            ).first()
    )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error.__dict__.get("orig", error))
        )

    order_count = result[0] if result else 0
    total_revenue = result[1] if result else Decimal("0.00")

    return {
        "report_date": report_date,
        "order_count": order_count,
        "total_revenue": total_revenue
    }


# Update
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


# Delete
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