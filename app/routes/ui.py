from fastapi import APIRouter, Request, Depends, Form, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.database import get_db
from app.models import Request as DBRequest, User, UserRole
from app.auth import verify_password
import os
import hashlib

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

templates = Jinja2Templates(directory="app/templates")

def get_current_user_from_cookie(user_id: int = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=303, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=303, detail="User not found")
    return user

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_handler(
    username: str = Form(...), 
    email: str = Form(...),
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        # Можно вернуть ошибку или редирект
        return HTMLResponse(
            content="<h1 style='color:red;'>Пользователь с таким логином уже есть!</h1><a href='/ui/register'>Назад</a>", 
            status_code=400
        )
    # 1. Настройки хэширования
    iterations = 600000
    salt = os.urandom(16)  # Генерируем уникальную соль для каждого юзера
    
    # 2. Создаем ключ
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    
    # 3. Собираем хэш в формат, который понимает твоя verify_password
    # Формат: algorithm$iterations$salt_hex$key_hex
    hashed_password = f"pbkdf2_sha256${iterations}${salt.hex()}${key.hex()}"
    
    # 4. Сохраняем в базу
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=UserRole.user
    )
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/ui/login", status_code=303)

# 4. Главная страница с заявками (GET)
@router.get("/requests", response_class=HTMLResponse)
async def ui_requests_page(
    request: Request,
    search: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(get_current_user_from_cookie), 
    db: Session = Depends(get_db)
):
    # Логика фильтрации
    query = db.query(DBRequest)
    if search:
        query = query.filter(
            (DBRequest.title.ilike(f"%{search}%")) | 
            (DBRequest.description.ilike(f"%{search}%"))
        )
    if status:
        query = query.filter(DBRequest.status == status)
        
    db_requests = query.all()
    
    # Передаем ВСЕ необходимые переменные в шаблон
    return templates.TemplateResponse("requests.html", {
        "request": request, 
        "requests": db_requests,
        "current_search": search or "",
        "current_status": status or "",
        "current_user": current_user,  # Теперь переменная доступна в шаблоне!
        "username": current_user.username
    })

# 5. Обработка создания новой заявки (POST)
@router.post("/requests/create")
async def ui_create_request(
    title: str = Form(...),
    description: str = Form(...),
    fio: str = Form(...),    # Получаем ФИО
    phone: str = Form(...),  # Получаем телефон
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    new_request = DBRequest(
        title=title, 
        description=description, 
        fio=fio,              # Сохраняем в БД
        phone=phone,          # Сохраняем в БД
        user_id=current_user.id,
        status="pending"
    )
    db.add(new_request)
    db.commit()
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
    current_user: User = Depends(get_current_user_from_cookie), # Используем нашу проверку
    db: Session = Depends(get_db)
):
    # Проверяем роль
    if current_user.role != UserRole.admin:
        # Если не админ, возвращаем ошибку или редирект
        return RedirectResponse(url="/ui/requests?error=forbidden", status_code=303)
        
    db_request = db.query(DBRequest).filter(DBRequest.id == request_id).first()
    if db_request:
        db_request.status = status
        db.commit()
            
    return RedirectResponse(url=f"/ui/requests/{request_id}", status_code=303)

@router.get("/logout")
async def ui_logout():
    response = RedirectResponse(url="/ui/login", status_code=303)
    # Намертво стираем куку авторизации
    response.delete_cookie(key="user_id")
    return response

# Добавь это в конец файла app/routes/ui.py

@router.get("/requests")
async def ui_requests_page(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    # Логика: если админ - берем все, если юзер - фильтруем по его ID
    if current_user.role == UserRole.admin:
        all_requests = db.query(DBRequest).all()
    else:
        all_requests = db.query(DBRequest).filter(DBRequest.user_id == current_user.id).all()
    
    return templates.TemplateResponse("requests.html", {
        "request": request, 
        "requests": all_requests,
        "current_user": current_user, 
        "username": current_user.username
    })