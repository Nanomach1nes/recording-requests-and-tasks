from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.database import get_db
from app.models import Category, RepairRequest, User, UserRole
from app.schemas import RequestCreate, RequestRead, RequestUpdate

router = APIRouter()


def is_admin(user: User) -> bool:
    role = getattr(user, "role", "")
    if hasattr(role, "value"):
        role = role.value
    return str(role).lower() == UserRole.admin.value

@router.get("/", response_model=list[RequestRead])
def list_requests(
    search: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(RepairRequest)
    if not is_admin(current_user):
        query = query.filter(RepairRequest.user_id == current_user.id)
    if search:
        query = query.filter(
            (RepairRequest.title.ilike(f"%{search}%"))
            | (RepairRequest.description.ilike(f"%{search}%"))
        )
    if status_filter:
        query = query.filter(RepairRequest.status == status_filter)
    return query.order_by(RepairRequest.id.desc()).all()

@router.get("/{request_id}", response_model=RequestRead)
def get_request(
    request_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = db.get(RepairRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if current_user.id != request.user_id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return request


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
    if not is_admin(current_user):
        payload.user_id = current_user.id

    request = RepairRequest(**payload.model_dump())
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
    request = db.get(RepairRequest, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if not is_admin(current_user) and request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для редактирования заявки")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        if db.get(Category, data["category_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.put("/{request_id}/status", response_model=RequestRead)
def update_request_status(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = db.get(RepairRequest, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if not is_admin(current_user) and request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для изменения статуса")
    if payload.status is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status is required")

    request.status = payload.status
    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = db.get(RepairRequest, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if not is_admin(current_user) and request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для удаления заявки")

    db.delete(request)
    db.commit()