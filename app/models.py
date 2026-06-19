from sqlalchemy import Column, Integer, String, Enum
from metadata import Base
print(f"Модель User импортирует Base: {Base}")
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.user)

class Request(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    fio = Column(String)         
    phone = Column(String)
    status = Column(String, default="pending")
    user_id = Column(Integer) # или ForeignKey, если нужно