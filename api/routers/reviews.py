from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..controllers import reviews as controller
from ..dependencies.database import get_db
from ..schemas import review as schema

router = APIRouter(
    prefix = "/reviews",
    tags = ["Reviews"]
)

