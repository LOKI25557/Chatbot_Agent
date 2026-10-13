from fastapi import APIRouter
from app.api.v1.books import router as books_router
from app.api.v1.search import router as search_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(books_router)
api_router.include_router(search_router)
api_router.include_router(admin_router)
