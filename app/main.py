
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import get_db
from app.database import Base, engine
from app import models
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    CustomerListResponse,
)
from app.api.routes.customers import router as customers_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAPI PostgreSQL CRUD",
    description="API quản lý khách hàng",
    version="1.0.0",
)

app.include_router(customers_router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "FastAPI is running"}


@app.get("/health/db")
def check_database():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        ).one()

    return {
        "database": result[0],
        "user": result[1],
        "status": "connected",
    }


