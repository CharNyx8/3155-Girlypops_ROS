from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import customer as controller
from ..dependencies.database import get_db
from ..schemas import customer as schema


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post(
    "/",
    response_model=schema.CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    request: schema.CustomerCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.CustomerResponse]
)
def read_all_customers(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/{customer_id}",
    response_model=schema.CustomerResponse
)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, customer_id=customer_id)


@router.put(
    "/{customer_id}",
    response_model=schema.CustomerResponse
)
def update_customer(
    customer_id: int,
    request: schema.CustomerUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, customer_id=customer_id, request=request)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, customer_id=customer_id)