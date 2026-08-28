from fastapi import APIRouter, Path, status
from schemas.external import PostResponse
from services.external_service import get_external_post

router = APIRouter(prefix="/external", tags=["External Services"])


@router.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
async def get_post_by_id(
    post_id: int = Path(..., ge=1, description="The ID of the post to retrieve")
):
    return await get_external_post(post_id)
