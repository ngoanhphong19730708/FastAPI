
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    CustomerListResponse,
)
from app.services import customer_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get("/", response_model=CustomerListResponse)
def get_customers(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return customer_service.get_customers(
        db=db,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        customer = customer_service.create_customer(
            db=db,
            name=customer_data.name,
            email=str(customer_data.email),
            phone=customer_data.phone,
        )
        return customer

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except IntegrityError:
        db.rollback()
        logger.warning(
            "Customer creation failed due to a database constraint"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists or data violates a database constraint",
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating customer")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return customer_service.get_customer_by_id(
            db=db,
            customer_id=customer_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        return customer_service.update_customer(
            db=db,
            customer_id=customer_id,
            name=customer_data.name,
            email=str(customer_data.email),
            phone=customer_data.phone,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except IntegrityError:
        db.rollback()
        logger.warning("Customer update failed due to a database constraint")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists or data violates a database constraint",
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while updating customer")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted_id = customer_service.delete_customer(
            db=db,
            customer_id=customer_id,
        )

        return {
            "message": "Customer deleted successfully",
            "id": deleted_id,
        }

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while deleting customer")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
