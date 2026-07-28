from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import employee as controller
from ..dependencies.database import get_db
from ..schemas import employee as schema

router = APIRouter(
    prefix="/employee",
    tags=["Restaurant Employees"]
)

@router.post(
    "/",
    response_model=schema.RestaurantEmployeeSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
        request: schema.EmployeeCreate,
        db: Session = Depends(get_db)
):
    return controller.create(
        db=db,
        request=request
    )

@router.get(
    "/",
    response_model=list[schema.RestaurantEmployeeSchema]
)
def read_all_employees(
    db: Session = Depends(get_db)
):
    return controller.read_all(db)

@router.get(
    "/{employee_id}",
    response_model=schema.RestaurantEmployeeSchema
)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    return controller.read_one(
        db=db,
        employee_id=employee_id
    )

@router.put(
    "/{employee_id}",
    response_model=schema.RestaurantEmployeeSchema
)
def update_employee(
    employee_id: int,
    request: schema.EmployeeUpdate,
    db: Session = Depends(get_db)
):
    return controller.update(
        db=db,
        employee_id=employee_id,
        request=request
    )

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    return controller.delete(
        db=db,
        employee_id=employee_id
    )