from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.inventory import Inventory
from ..schemas import inventory as schema

def create(db: Session, request: schema.InventoryCreate):
    new_item = Inventory(**request.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def read_all(db: Session):
    return db.query(Inventory).all()

def read_one(db: Session, ingredient_id: int):
    item = db.query(Inventory).filter(Inventory.ingredient_id == ingredient_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {ingredient_id} not found",
        )
    return item


def update(db: Session, ingredient_id: int, request: schema.InventoryUpdate):
    item = read_one(db=db, ingredient_id=ingredient_id)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

def delete(db: Session, ingredient_id: int):
    item = read_one(db=db, ingredient_id=ingredient_id)
    db.delete(item)
    db.commit()
    return None