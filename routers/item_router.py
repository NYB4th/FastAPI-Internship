from fastapi import APIRouter, HTTPException, status
from schmeas.item import ItemRead
from services import item_service

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=list[ItemRead], status_code=status.HTTP_200_OK)
def get_all():
    return item_service.get_all_items()


@router.get("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
def get_by_id(item_id: int):
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="item not found"
        )
    return item
