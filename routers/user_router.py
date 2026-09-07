from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.user import User
from schemas.error import ErrorResponse
from schemas.user import UserResponse, UserRoleUpdate
from services.user_service import update_user_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user role",
    description="Updates a user's role (user or admin). Admin access required.",
    responses={
        401: {"description": "Missing or invalid authentication token."},
        403: {"description": "Operation not permitted. Requires admin role."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return update_user_role(db=db, user_id=user_id, role_data=role_data)
