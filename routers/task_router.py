from fastapi import APIRouter, status
from schmeas.task import TaskRead, TaskCreate
from services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    return task_service.create_task(task_in)


@router.get("", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_all():
    return task_service.get_all_tasks()


@router.get("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
def get_by_id(task_id: int):
    return task_service.get_task_by_id(task_id)
