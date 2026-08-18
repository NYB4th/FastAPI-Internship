from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.task import TaskRead, TaskCreate, TaskUpdate
from services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(task_in, db)


@router.get("", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_all(
    limit: int = Query(10, ge=1, le=100, description="Max number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    db: Session = Depends(get_db),
):
    return task_service.get_all_tasks(db, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
def get_by_id(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task_by_id(task_id, db)


@router.put("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    return task_service.update_task(task_id, task_in, db)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service.delete_task(task_id, db)
