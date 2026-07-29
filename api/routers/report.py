from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import date

from ..controllers import report as controller
from ..dependencies.database import get_db
from ..schemas import report as schema


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post(
    "/",
    response_model=schema.Report,
    status_code=status.HTTP_201_CREATED
)
def create_report(
    request: schema.ReportCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.Report]
)
def read_all_reports(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/daily-revenue",
    response_model=schema.DailyRevenue
)
def read_daily_revenue(
    report_date: date,
    db: Session = Depends(get_db)
):
    return controller.read_daily_revenue(
        db=db,
        report_date=report_date
    )


@router.get(
    "/{report_id}",
    response_model=schema.Report
)
def read_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, report_id=report_id)


@router.put(
    "/{report_id}",
    response_model=schema.Report
)
def update_report(
    report_id: int,
    request: schema.ReportUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, report_id=report_id, request=request)


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, report_id=report_id)