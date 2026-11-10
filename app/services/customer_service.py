
from sqlalchemy.orm import Session

from app.repositories import customer_repository


def create_customer(
    db: Session,
    name: str,
    email: str,
    phone: str | None,
):
    existing_customer = customer_repository.get_by_email(
        db,
        email,
    )

    if existing_customer:
        raise ValueError("Email already exists")

    try:
        customer = customer_repository.create(
            db,
            {
                "name": name,
                "email": email,
                "phone": phone,
            },
        )

        db.commit()
        db.refresh(customer)

        return customer

    except Exception:
        db.rollback()
        raise


def get_customer_by_id(
    db: Session,
    customer_id: int,
):
    customer = customer_repository.get_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    return customer


def get_customers(
    db: Session,
    search: str | None,
    page: int,
    page_size: int,
):
    return customer_repository.get_list(
        db=db,
        search=search,
        page=page,
        page_size=page_size,
    )


def update_customer(
    db: Session,
    customer_id: int,
    name: str,
    email: str,
    phone: str | None,
):
    customer = customer_repository.get_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    existing_customer = customer_repository.get_by_email(
        db,
        email,
    )

    if existing_customer and existing_customer.id != customer_id:
        raise ValueError("Email already exists")

    try:
        updated_customer = customer_repository.update(
            db,
            customer,
            {
                "name": name,
                "email": email,
                "phone": phone,
            },
        )
        db.commit()
        db.refresh(updated_customer)

        return updated_customer

    except Exception:
        db.rollback()
        raise

def delete_customer(
    db: Session,
    customer_id: int,
) -> int:
    customer = customer_repository.get_by_id(
        db,
        customer_id,
    )

    if customer is None:
        raise LookupError("Customer not found")

    try:
        customer_repository.delete(db, customer)
        db.commit()
        return customer_id
    except Exception:
        db.rollback()
        raise