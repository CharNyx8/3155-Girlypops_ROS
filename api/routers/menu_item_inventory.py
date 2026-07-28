from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..controllers import menu_item_inventory as controller
from ..dependencies.database import get_db
from ..schemas import menu_item_inventory as schema


router = APIRouter(
    prefix="/menu-item-inventory",
    tags=["Menu Item Inventory"]
)


@router.post(
    "/",
    response_model=schema.MenuItemInventory,
    status_code=status.HTTP_201_CREATED
)
def create_menu_item_inventory_link(
    request: schema.MenuItemInventoryCreate,
    db: Session = Depends(get_db)
):
    return controller.create(db=db, request=request)


@router.get(
    "/",
    response_model=list[schema.MenuItemInventory]
)
def read_all_menu_item_inventory_links(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)


@router.get(
    "/{item_id}/{ingredient_id}",
    response_model=schema.MenuItemInventory
)
def read_menu_item_inventory_link(
    item_id: int,
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(
        db=db,
        item_id=item_id,
        ingredient_id=ingredient_id
    )


@router.put(
    "/{item_id}/{ingredient_id}",
    response_model=schema.MenuItemInventory
)
def update_menu_item_inventory_link(
    item_id: int,
    ingredient_id: int,
    request: schema.MenuItemInventoryUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(
        db=db,
        item_id=item_id,
        ingredient_id=ingredient_id,
        request=request
    )


@router.delete(
    "/{item_id}/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_menu_item_inventory_link(
    item_id: int,
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(
        db=db,
        item_id=item_id,
        ingredient_id=ingredient_id
    )