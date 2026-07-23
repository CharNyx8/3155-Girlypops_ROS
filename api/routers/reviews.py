from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import reviews as controller
from ..dependencies.database import get_db
from ..schemas import review as schema

router = APIRouter(
    prefix = "/reviews",
    tags = ["Reviews"]
)

@router.post(
    "/",
    response_model = schema.ReviewResponse,
    status_code = status.HTTP_201_CREATED
)

def create_review(
        request: schema.ReviewCreate,
        db:Session = Depends(get_db)
):
    return controller.create(db=db, request=request)

@router.get(
    "/",
    response_model = list[schema.ReviewResponse]
)
def read_all_reviews(
        db:Session = Depends(get_db)
):
    return controller.read_all(db)

@router.get(
    "/menu-item/{item_id}",
    response_model = list[schema.ReviewResponse],
)
def read_reviews_for_menu_item(
        item_id: int,
        db:Session = Depends(get_db)
):
    return controller.read_by_menu_item(
        db=db,
        item_id=item_id
    )

@router.get(
    "/{review_id}",
    response_model = schema.ReviewResponse,
)
def read_review(
        review_id: int,
        db: Session = Depends(get_db)
):
    return controller.read_one(
        db=db,
        review_id = review_id
    )
@router.put(
    "/{review_id}",
    response_model = schema.ReviewResponse,
)
def update_review(
        review_id: int,
        request: schema.ReviewUpdate,
        db:Session = Depends(get_db)
):
    return controller.update(
        db=db,
        review_id = review_id,
        request=request

    )
@router.delete(
    "/{review_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_review(
        review_id: int,
        db:Session = Depends(get_db)
):
    return controller.delete(
        db=db,
        review_id = review_id
    )