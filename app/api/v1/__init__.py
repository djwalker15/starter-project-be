from fastapi import APIRouter

from .greeting import router as greeting_router

api_v1 = APIRouter()
api_v1.include_router(greeting_router)
