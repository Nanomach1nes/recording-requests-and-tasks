from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryRead
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).all()

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category