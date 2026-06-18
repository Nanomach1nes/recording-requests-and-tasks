import hashlib
import os
from app.database import SessionLocal, init_db
from app.models import User, UserRole

def generate_secure_hash(password: str) -> str:
    """Хэширует пароль через PBKDF2 SHA256 (стандарт без внешних зависимостей)"""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Форматируем в строку, чтобы легко хранить в текстовом поле БД
    return f"pbkdf2_sha256$100000${salt.hex()}${key.hex()}"

def seed_data():
    print("Инициализация таблиц в PostgreSQL...")
    init_db()  # Создает все таблицы через SQLAlchemy
    
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже пользователи в базе
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("Создание дефолтного пользователя admin...")
            # Хэшируем наш любимый пароль 'postgres'
            hashed_password = generate_secure_hash("postgres")
            
            admin_user = User(
                username="admin",
                email="admin@example.com",  # ДОБАВИЛИ ОБЯЗАТЕЛЬНОЕ ПОЛЕ
                hashed_password=hashed_password,
                role=UserRole.admin if hasattr(UserRole, "admin") else "admin"
            )
            db.add(admin_user)
            db.commit()
            print("Пользователь admin успешно добавлен! Пароль: postgres")
        else:
            print("Пользователь admin уже существует в базе.")
            
    except Exception as e:
        print(f"Произошла ошибка при заполнении базы: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()