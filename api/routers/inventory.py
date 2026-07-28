from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import inventory as controller
from ..dependencies.database import get_db
from ..schemas import inventory as schema


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.post(
    "/",
    response_model=schema.Inventory,
    status_code=status.HTTP_201_CREATED
)
def create_inventory_item(
    request: schema.InventoryCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.Inventory]
)
def read_all_inventory_items(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/{ingredient_id}",
    response_model=schema.Inventory
)
def read_inventory_item(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(db=db, ingredient_id=ingredient_id)


@router.put(
    "/{ingredient_id}",
    response_model=schema.Inventory
)
def update_inventory_item(
    ingredient_id: int,
    request: schema.InventoryUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(db=db, ingredient_id=ingredient_id, request=request)


@router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_inventory_item(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(db=db, ingredient_id=ingredient_id)