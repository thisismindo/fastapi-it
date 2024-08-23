from fastapi import APIRouter
from .users import UserRouter

api_router = APIRouter()

user_router = UserRouter()

api_router.include_router(user_router.router, prefix="/users", tags=["users"])
