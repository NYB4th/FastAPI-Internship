from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from exceptions.auth_exceptions import UserAlreadyExistsError
from models.user import User
from schemas.user import UserCreate, UserRoleUpdate
from utils.security import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise UserAlreadyExistsError(email=user_data.email)

    hashed_pwd = hash_password(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed_pwd)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user


def update_user_role(db: Session, user_id: int, role_data: UserRoleUpdate) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    user.role = role_data.role  # pyright: ignore[reportAttributeAccessIssue]
    db.commit()
    db.refresh(user)
    return user
