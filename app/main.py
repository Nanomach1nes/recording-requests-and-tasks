from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles  # Импортируем для статики
from fastapi.templating import Jinja2Templates  # Импортируем для HTML
from app.database import engine, Base
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.models import User, UserRole

from app.routes import auth, requests, tasks, categories, comments
from app.routes.ui import router as ui_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Система учёта заявок и задач",
    description="API для управления заявками и связанными задачами",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ui_router, prefix="/ui", tags=["ui"])

# Настраиваем шаблоны и статику (папки, которые ты создал)
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(requests.router, prefix="/api/v1/requests", tags=["requests"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(ui_router, prefix="/ui", tags=["ui"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root_redirect():
    return RedirectResponse(url="/ui/login")