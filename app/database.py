import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.metadata import Base

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Удалили импорт моделей сюда, чтобы избежать циклов
# Запуск создания таблиц:
if __name__ == "__main__":
    from app.models import User, RepairRequest 
    print(f"Модели импортированы. Метаданные содержат таблицы: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=engine)
    print("Команда создания выполнена.")