from fastapi import APIRouter, Request, Depends, Form, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.database import get_db
from app.models import Request as DBRequest, User

# 1. Сначала создаём объект роутера и настраиваем шаблоны
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 2. Страница авторизации (GET)
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 3. Обработка отправки формы логина (POST)
@router.post("/login")
async def ui_login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/ui/login?error=Invalid+credentials", status_code=303)
    
    response = RedirectResponse(url="/ui/requests", status_code=303)
    # Ставим куку с ID пользователя
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response

# 4. Главная страница с заявками (GET)
@router.get("/requests", response_class=HTMLResponse)
def requests_page(
    request: Request,
    search: str = Query(None),
    status: str = Query(None),
    user_id: str = Cookie(None),  # Получаем куку текущего юзера
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/ui/login", status_code=303)
        
    # Ищем пользователя в базе, чтобы вытащить его username
    current_user = db.query(User).filter(User.id == int(user_id)).first()
    username = current_user.username if current_user else "Пользователь"

    query = db.query(DBRequest)
    if search:
        query = query.filter(
            (DBRequest.title.ilike(f"%{search}%")) | 
            (DBRequest.description.ilike(f"%{search}%"))
        )
    if status:
        query = query.filter(DBRequest.status == status)
        
    db_requests = query.all()
    
    return templates.TemplateResponse(
        "requests.html", 
        {
            "request": request, 
            "requests": db_requests,
            "current_search": search or "",
            "current_status": status or "",
            "username": username  # Передаём имя в HTML
        }
    )

# 5. Обработка создания новой заявки (POST)
@router.post("/requests/create")
async def ui_create_request(
    title: str = Form(...),
    description: str = Form(...),
    user_id: str = Cookie(None),  # Вытаскиваем ID авторизованного юзера из куки
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/ui/login", status_code=303)
        
    try:
        new_request = DBRequest(
            title=title,
            description=description,
            user_id=int(user_id),  # Привязываем к нашему админу
            status="pending"
        )
        db.add(new_request)
        db.commit()
    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/ui/requests?error=db_error", status_code=303)

    return RedirectResponse(url="/ui/requests", status_code=303)

# Добавь этот роут в app/routes/ui.py для открытия карточки заявки

@router.get("/requests/{request_id}", response_class=HTMLResponse)
def view_request_page(request_id: int, request: Request, db: Session = Depends(get_db)):
    # Ищем конкретную заявку в базе
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    
    if not db_request:
        return HTMLResponse(content="<h1>Заявка не найдена в базе данных</h1>", status_code=404)
        
    # Передаем её в отдельный шаблон (например, request_detail.html)
    # Если отдельного шаблона нет, давай пока просто вернем её данные красивым JSON или простеньким HTML
    return templates.TemplateResponse(
        "request_detail.html", 
        {"request": request, "req": db_request}
    )

@router.post("/requests/{request_id}/status")
async def ui_update_request_status(
    request_id: int,
    status: str = Form(...),
    user_id: str = Cookie(None),  # Проверяем авторизацию
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/ui/login", status_code=303)
        
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    
    if db_request:
        try:
            db_request.status = status  # Меняем статус на выбранный
            db.commit()
        except Exception:
            db.rollback()
            return RedirectResponse(url=f"/ui/requests/{request_id}?error=update_failed", status_code=303)
            
    return RedirectResponse(url=f"/ui/requests/{request_id}", status_code=303)

@router.get("/logout")
async def ui_logout():
    response = RedirectResponse(url="/ui/login", status_code=303)
    # Намертво стираем куку авторизации
    response.delete_cookie(key="user_id")
    return response