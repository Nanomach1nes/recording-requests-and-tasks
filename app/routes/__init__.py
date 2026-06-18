from fastapi import APIRouter

from app.routes import auth, requests, tasks, categories, comments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])