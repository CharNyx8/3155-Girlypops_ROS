from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import payments as controller
from ..dependencies.database import get_db
from ..schemas import payments as schema


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post(
    "/",
    response_model=schema.Payment,
    status_code=status.HTTP_201_CREATED
)
def create_payment(
    request: schema.PaymentCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.Payment]
)
def read_all_payments(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/{payment_id}",
    response_model=schema.Payment
)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, payment_id=payment_id)


@router.put(
    "/{payment_id}",
    response_model=schema.Payment
)
def update_payment(
    payment_id: int,
    request: schema.PaymentUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, payment_id=payment_id, request=request)


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, payment_id=payment_id)