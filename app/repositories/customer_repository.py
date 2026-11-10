
from sqlalchemy.orm import Session

from app import models


def get_by_id(db: Session, customer_id: int):
    return (
        db.query(models.Customer)
        .filter(models.Customer.id == customer_id)
        .first()
    )


def get_by_email(db: Session, email: str):
    return (
        db.query(models.Customer)
        .filter(models.Customer.email == email)
        .first()
    )


def create(db: Session, customer_data: dict):
    customer = models.Customer(**customer_data)

    db.add(customer)
    db.flush()
    db.refresh(customer)

    return customer


def get_list(
    db: Session,
    search: str | None,
    page: int,
    page_size: int,
):
    query = db.query(models.Customer)

    if search:
        keyword = f"%{search.strip()}%"
        query = query.filter(
            models.Customer.name.ilike(keyword)
            | models.Customer.email.ilike(keyword)
        )

    total = query.count()

    total_pages = (total + page_size - 1) // page_size

    customers = (
        query.order_by(models.Customer.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": customers,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def update(
    db: Session,
    customer: models.Customer,
    customer_data: dict,
):
    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.flush()
    db.refresh(customer)

    return customer


def delete(db: Session, customer: models.Customer) -> None:
    db.delete(customer)
    db.flush()
