from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Request, User
from app.schemas import RequestCreate, RequestRead, RequestUpdate

router = APIRouter()


@router.get("/", response_model=list[RequestRead])
def list_requests(db: Session = Depends(get_db)):
    return db.query(Request).order_by(Request.id.desc()).all()


@router.get("/{request_id}", response_model=RequestRead)
def get_request(request_id: int, db: Session = Depends(get_db)):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request


@router.post("/", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: Session = Depends(get_db)):
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.category_id is not None and db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    request = Request(**payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.patch("/{request_id}", response_model=RequestRead)
def update_request(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        if db.get(Category, data["category_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    db.delete(request)
    db.commit()
