from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import promo_codes as controller
from ..dependencies.database import get_db
from ..schemas import promo_codes as schema


router = APIRouter(
    prefix="/promo-codes",
    tags=["Promo Codes"]
)


@router.post(
    "/",
    response_model=schema.PromoCode,
    status_code=status.HTTP_201_CREATED
)
def create_promo_code(
    request: schema.PromoCodeCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.PromoCode]
)
def read_all_promo_codes(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/{promo_code}",
    response_model=schema.PromoCode
)
def read_promo_code(
    promo_code: str,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, promo_code=promo_code)


@router.put(
    "/{promo_code}",
    response_model=schema.PromoCode
)
def update_promo_code(
    promo_code: str,
    request: schema.PromoCodeUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, promo_code=promo_code, request=request)


@router.delete(
    "/{promo_code}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_promo_code(
    promo_code: str,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, promo_code=promo_code)