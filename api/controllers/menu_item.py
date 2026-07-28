from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.menu_item import MenuItem
from ..schemas import menu_item as schema

def create(db: Session, request: schema.MenuItemCreate):
    new_item = MenuItem(**request.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def read_all(db: Session):
    return db.query(MenuItem).all()

def read_one(db: Session, item_id: int):
    item = db.query(MenuItem).filter(MenuItem.item_id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {item_id} not found",
        )
    return item


def update(db: Session, item_id: int, request: schema.MenuItemUpdate):
    item = read_one(db=db, item_id=item_id)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

def delete(db: Session, item_id: int):
    item = read_one(db=db, item_id=item_id)
    db.delete(item)
    db.commit()
    return None