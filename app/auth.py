from fastapi import Request
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Ищет пользователя по ID, который мы сохранили в куки при логине"""
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user