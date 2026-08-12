from common.exceptions import AppException
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text

from middleware.logging import LoggingMiddleware
from modules.users.router import router as user_router
from modules.auth.router import router as auth_router
from modules.projects.router import router as project_router
from modules.reviews.router import router as review_router
from db.database import engine
from common.handlers import app_exception_handler, validation_exception_handler, generic_exception_handler
from modules.ai.router import router as ai_router
from modules.comments.router import router as comment_router
from modules.notifications.router import router as notification_router
from modules.search.router import router as search_router

app = FastAPI()


@app.get("/")
def test_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    return {
        "message": "Connected PostgreSQL"
    }

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(review_router)

app.add_exception_handler(
    AppException,
    app_exception_handler
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)
app.add_exception_handler(
    Exception,
    generic_exception_handler
)

app.add_middleware(
    LoggingMiddleware
)

app.include_router(ai_router)
app.include_router(comment_router)
app.include_router(notification_router)
app.include_router(search_router)