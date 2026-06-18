from fastapi import APIRouter

from app.routes import auth, requests, tasks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
