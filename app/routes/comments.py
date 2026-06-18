from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Request, User
from app.schemas import CommentCreate, CommentRead
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/request/{request_id}", response_model=list[CommentRead])
def list_comments_for_request(
    request_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, существует ли вообще такая заявка
    request = db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    # Возвращаем все комментарии к ней
    return db.query(Comment).filter(Comment.request_id == request_id).order_by(Comment.id.asc()).all()

@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем существование заявки
    if db.get(Request, payload.request_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    # Принудительно привязываем комментарий к текущему авторизованному юзеру
    payload.user_id = current_user.id

    comment = Comment(**payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment