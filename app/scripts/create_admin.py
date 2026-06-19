# scripts/create_admin.py
from app.database import SessionLocal
from app.models import User, UserRole
# ... импорт функции хеширования пароля ...

def create_admin_user(email, password):
    db = SessionLocal()
    # ... логика создания пользователя с хешированием ...
    print("Администратор успешно создан!")
    db.close()