from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.metadata import Base

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/recording_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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
    from app.models import User, Request 
    print(f"Модели импортированы. Метаданные содержат таблицы: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=engine)
    print("Команда создания выполнена.")