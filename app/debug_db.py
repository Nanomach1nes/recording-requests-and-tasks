from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metadata import Base  # Импортируем напрямую, так как они в одной папке
from models import User, RepairRequest # Импортируем напрямую

# Добавляем корень проекта в пути поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь импортируем через путь app.models, так как мы добавили корень в sys.path
from app.models import Base, User, RepairRequest
print("Запускаю принудительное создание таблиц...")
Base.metadata.drop_all(bind=engine) # Удаляет ВСЕ существующие таблицы
Base.metadata.create_all(bind=engine) # Создает их заново строго по коду из models.py
print("Готово. Проверь структуру таблицы requests.")