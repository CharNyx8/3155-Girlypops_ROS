from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.menu_item_inventory import MenuItemInventory
from ..schemas import menu_item_inventory as schema


def create(db: Session, request: schema.MenuItemInventoryCreate):
    new_link = MenuItemInventory(**request.model_dump())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link


def read_all(db: Session):
    return db.query(MenuItemInventory).all()


def read_one(db: Session, item_id: int, ingredient_id: int):
    link = (
        db.query(MenuItemInventory)
        .filter(
            MenuItemInventory.item_id == item_id,
            MenuItemInventory.ingredient_id == ingredient_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link between menu item {item_id} and ingredient {ingredient_id} not found",
        )
    return link


def update(db: Session, item_id: int, ingredient_id: int, request: schema.MenuItemInventoryUpdate):
    link = read_one(db=db, item_id=item_id, ingredient_id=ingredient_id)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)

    db.commit()
    db.refresh(link)
    return link


def delete(db: Session, item_id: int, ingredient_id: int):
    link = read_one(db=db, item_id=item_id, ingredient_id=ingredient_id)
    db.delete(link)
    db.commit()
    return None