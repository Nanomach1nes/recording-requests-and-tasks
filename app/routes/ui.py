from fastapi import APIRouter, Request, Depends, Form, Cookie, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RepairRequest as DBRequest, User, UserRole
from app.auth import verify_password
import os
import hashlib

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def is_admin(user) -> bool:
    role = getattr(user, "role", "")
    if hasattr(role, "value"):
        role = role.value
    return str(role).lower().strip() == "admin"

def get_current_user_from_cookie(user_id: int = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=303, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=303, detail="User not found")
    return user

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def ui_login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": {}, "error": "Неверное имя пользователя или пароль"})
    response = RedirectResponse(url="/ui/requests", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@router.get("/logout")
async def ui_logout():
    response = RedirectResponse(url="/ui/login", status_code=303)
    response.delete_cookie(key="user_id")
    return response

@router.get("/requests", response_class=HTMLResponse)
async def ui_requests_page(
    request: Request,
    search: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(get_current_user_from_cookie), 
    db: Session = Depends(get_db)
):
    if is_admin(current_user):
        query = db.query(DBRequest)
    else:
        query = db.query(DBRequest).filter(DBRequest.user_id == current_user.id)

    if search:
        query = query.filter(
            (DBRequest.title.ilike(f"%{search}%")) | 
            (DBRequest.description.ilike(f"%{search}%"))
        )
    if status:
        query = query.filter(DBRequest.status == status)
        
    db_requests = query.all()
    
    return templates.TemplateResponse("requests.html", {
        "request": request, 
        "requests": db_requests,
        "current_search": search or "",
        "current_status": status or "",
        "current_user": current_user,  
        "username": current_user.username
    })

@router.post("/requests/create")
async def ui_create_request(
    title: str = Form(...),
    description: str = Form(...),
    fio: str = Form(...),
    phone: str = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    new_request = DBRequest(
        title=title,
        description=description,
        fio=fio,
        phone=phone,
        user_id=current_user.id,
        status="pending"
    )
    db.add(new_request)
    db.commit()
    return RedirectResponse(url="/ui/requests", status_code=303)

@router.get("/requests/{request_id}", response_class=HTMLResponse)
def view_request_page(request_id: int, request: Request, db: Session = Depends(get_db)):
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    if not db_request:
        return HTMLResponse(content="<h1>Заявка не найдена в базе данных</h1>", status_code=404)
    return templates.TemplateResponse(
        "request_detail.html", 
        {"request": request, "req": db_request}
    )

@router.post("/requests/{request_id}/status")
async def ui_update_request_status(
    request_id: int,
    status: str = Form(...),
    current_user: User = Depends(get_current_user_from_cookie), 
    db: Session = Depends(get_db)
):
    if not is_admin(current_user):
        return RedirectResponse(url="/ui/requests?error=forbidden", status_code=303)
        
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    if db_request:
        db_request.status = status
        db.commit()
            
    return RedirectResponse(url=f"/ui/requests/{request_id}", status_code=303)

@router.post("/requests/{request_id}/delete")
async def ui_delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    if not is_admin(current_user):
        return RedirectResponse(url="/ui/requests?error=forbidden", status_code=303)
        
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    if db_request:
        db.delete(db_request)
        db.commit()
        
    return RedirectResponse(url="/ui/requests", status_code=303)