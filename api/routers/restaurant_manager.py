from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import restaurant_manager as controller
from ..dependencies.database import get_db
from ..schemas import restaurant_manager as schema

router = APIRouter(
    prefix="/restaurant-manager ",
    tags=["Restaurant Manager"],
)

@router.post(
    "/",
    response_model=schema.RestaurantManager,
    status_code=status.HTTP_201_CREATED
)
def create_manager(
    request: schema.RestaurantManagerCreate,
    db: Session = Depends(get_db)
):
    return controller.create(
        db=db,
        request=request
    )

@router.get(
    "/",
    response_model=list[schema.RestaurantManager]
)
def read_all_managers(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)

@router.get(
    "/{manager_id}",
    response_model=schema.RestaurantManager
)
def read_manager(
    manager_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(
        db=db,
        manager_id=manager_id
    )

@router.put(
    "/{manager_id}",
    response_model=schema.RestaurantManager
)
def update_manager(
    manager_id: int,
    request: schema.RestaurantManagerUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(
        db=db,
        manager_id=manager_id,
        request=request
    )


@router.delete(
    "/{manager_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_manager(
    manager_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(
        db=db,
        manager_id=manager_id
    )

