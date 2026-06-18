from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Request as DBRequest  # Импортируем модель заявки
# Указываем относительный путь к шаблонам от корня проекта
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# 1. Страница авторизации (GET)
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 2. Обработка отправки формы логина (POST)
@router.post("/login")
async def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Пока что делаем простую заглушку для проверки перехода
    # Если ввёл наш любимый пароль - пускаем дальше
    if username and password == "postgres":
        return RedirectResponse(url="/ui/requests", status_code=303)
    
    # Если что-то не так, возвращаем на ту же страницу с ошибкой
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "error": "Неверное имя пользователя или пароль"}
    )

# 3. Заглушка для главной страницы с заявками (GET)
@router.get("/requests", response_class=HTMLResponse)
def requests_page(request: Request, db: Session = Depends(get_db)):
    # Вытаскиваем абсолютно все заявки из базы данных
    db_requests = db.query(DBRequest).all()
    
    # Передаем их в шаблон под переменной "requests"
    return templates.TemplateResponse(
        "requests.html", 
        {"request": request, "requests": db_requests}
    )

@router.post("/requests/create")
async def ui_create_request(
    title: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    # Создаем объект заявки (пока без привязки к юзеру для простоты теста)
    new_request = DBRequest(title=title, description=description, status="pending")
    db.add(new_request)
    db.commit()
    
    # Возвращаем пользователя обратно на журнал заявок
    return RedirectResponse(url="/ui/requests", status_code=303)