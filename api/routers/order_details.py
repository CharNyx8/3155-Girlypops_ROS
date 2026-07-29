from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import order_details as controller
from ..dependencies.database import get_db
from ..schemas import order_details as schema


router = APIRouter(
    prefix="/order-details",
    tags=["Order Details"]
)


@router.post(
    "/",
    response_model=schema.OrderDetails,
    status_code=status.HTTP_201_CREATED
)
def create_order_detail(
    request: schema.OrderDetailsCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.OrderDetails]
)
def read_all_order_details(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/order/{order_id}",
    response_model=list[schema.OrderDetails]
)
def read_order_details_for_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_by_order(db=db, order_id=order_id)


@router.get(
    "/{order_detail_id}",
    response_model=schema.OrderDetails
)
def read_order_detail(
    order_detail_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(
        db=db,
        order_detail_id=order_detail_id
    )


@router.put(
    "/{order_detail_id}",
    response_model=schema.OrderDetails
)
def update_order_detail(
    order_detail_id: int,
    request: schema.OrderDetailsUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(
        db=db,
        order_detail_id=order_detail_id,
        request=request
    )


@router.delete(
    "/{order_detail_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_order_detail(
    order_detail_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(
        db=db,
        order_detail_id=order_detail_id
    )