from sqlalchemy.orm import Session

from exceptions.auth_exceptions import UserAlreadyExistsError
from models.user import User
from schemas.user import UserCreate
from utils.security import hash_password


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
