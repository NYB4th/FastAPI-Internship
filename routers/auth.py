from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserCreate, UserResponse
from services.user_service import create_user, authenticate_user

from schemas.token import Token
from utils.security import create_access_token
from schemas.error import ErrorResponse

from dependencies.rate_limiter import rate_limit_login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account using an email address and password.",
    response_description="User account created successfully.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "User with this email already exists.",
        }
    },
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user_data=user_data)


@router.post(
    "/token",
    response_model=Token,
    summary="Login for access token",
    description="Authenticates user credentials and returns a Bearer OAuth2 JWT token.",
    response_description="Access token generated successfully.",
    responses={
        401: {"model": ErrorResponse, "description": "Incorrect email or password."},
        429: {"model": ErrorResponse, "description": "Too many login attempts."},
    },
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_login),
):
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
