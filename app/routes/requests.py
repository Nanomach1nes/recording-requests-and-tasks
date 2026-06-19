from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import Category, Request, User, UserRole
from app.schemas import RequestCreate, RequestRead, RequestUpdate

router = APIRouter()

@router.get("/", response_model=list[RequestRead])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.admin or getattr(current_user.role, "value", "") == "admin":
        return db.query(Request).order_by(Request.id.desc()).all()
    return db.query(Request).filter(Request.user_id == current_user.id).order_by(Request.id.desc()).all()

@router.get("/{request_id}", response_model=RequestRead)
def get_request(
    request_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if current_user.id != request.user_id and current_user.role != UserRole.admin and getattr(current_user.role, "value", "") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return request

# ... остальные методы (POST, PATCH, DELETE) оставь как есть, они нормальные ...


@router.post("/", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: RequestCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.category_id is not None and db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Безопасность: обычный пользователь не может создавать заявки для чужих id
    if current_user.role != UserRole.admin and getattr(current_user.role, "value", "") != "admin":
        payload.user_id = current_user.id

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
    current_user: User = Depends(get_current_user)
):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if current_user.id != request.user_id and current_user.role != UserRole.admin and getattr(current_user.role, "value", "") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

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
def delete_request(
    request_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if current_user.id != request.user_id and current_user.role != UserRole.admin and getattr(current_user.role, "value", "") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db.delete(request)
    db.commit()