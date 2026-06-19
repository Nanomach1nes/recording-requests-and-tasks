from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from seed import generate_secure_hash
from fastapi import Form
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User, UserRole
from app.schemas import Token, UserRead, UserRegister

router = APIRouter()


@router.post("/register")
def register_worker(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Проверка, занят ли логин
    if db.query(User).filter(User.username == username).first():
        return RedirectResponse(url="/ui/login?error=exists", status_code=303)
    
    # Хэшируем пароль функцией из seed.py
    hashed_pw = generate_secure_hash(password)
    
    # Создаем нового пользователя
    new_user = User(
        username=username,
        email=f"{username}@work.local",
        hashed_password=hashed_pw,
        role=UserRole.user  # Убедись, что это роль обычного юзера
    )
    
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/ui/login", status_code=303)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError # Убедись, что эти библиотеки установлены

# Секретный ключ (у тебя он был в docker-compose)
SECRET_KEY = "super_secret_kpt_key_2026"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
