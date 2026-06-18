import os
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    """Хэширует пароль через безопасный PBKDF2 SHA256"""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хэшу из базы данных"""
    try:
        # Распиливаем строку хэша на составляющие
        algorithm, iterations, salt_hex, key_hex = hashed_password.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        
        salt = bytes.fromhex(salt_hex)
        # Хэшируем введённый пароль с той же солью
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, int(iterations))
        
        # Сравниваем старый хэш с новым
        return new_key.hex() == key_hex
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username  # Возвращаем СТРОКУ, а не словарь!
    except JWTError:
        return None
    
hash_password = get_password_hash