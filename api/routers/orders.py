from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import date

from ..controllers import orders as controller
from ..dependencies.database import get_db
from ..schemas import orders as schema


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/",
    response_model=schema.Order,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    request: schema.OrderCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.Order]
)
def read_all_orders(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get("/date-range", response_model=list[schema.Order])
def read_orders_by_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    return controller.read_by_date_range(db=db, start_date=start_date, end_date=end_date)


@router.get(
    "/{order_id}",
    response_model=schema.Order
)
def read_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, order_id=order_id)


@router.put(
    "/{order_id}",
    response_model=schema.Order
)
def update_order(
    order_id: int,
    request: schema.OrderUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, order_id=order_id, request=request)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, order_id=order_id)