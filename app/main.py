from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles  # Импортируем для статики
from fastapi.templating import Jinja2Templates  # Импортируем для HTML

from app.database import init_db
from app.routes import api_router
from app.routes.ui import router as ui_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Система учёта заявок и задач",
    description="API для управления заявками и связанными задачами",
    version="1.0.0",
    lifespan=lifespan,
)

# Настраиваем шаблоны и статику (папки, которые ты создал)
templates = Jinja2Templates(directory="app/templates")

app.include_router(api_router, prefix="/api/v1")
app.include_router(ui_router, prefix="/ui")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root_redirect():
    return RedirectResponse(url="/ui/login")