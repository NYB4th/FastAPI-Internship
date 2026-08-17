from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.task import TaskRead, TaskCreate
from services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(task_in, db)


@router.get("", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db)):
    return task_service.get_all_tasks(db)


@router.get("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
def get_by_id(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task_by_id(task_id, db)
