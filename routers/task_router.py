from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.error import ErrorResponse
from schemas.task import TaskCreate, TaskRead, TaskUpdate
from services import task_service
from services.audit import log_task_event

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task.",
    response_description="Task created successfully.",
    responses={
        401: {"description": "Missing or invalid authentication token."},
        409: {
            "model": ErrorResponse,
            "description": "Task with this title already exists.",
        },
    },
)
def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_service.create_task(task_in, db, user_id=(current_user.id))  # type: ignore
    background_tasks.add_task(
        log_task_event,
        task_id=task.id,  # pyright: ignore[reportArgumentType]
        user_id=task.user_id,  # pyright: ignore[reportArgumentType]
        event_type="TASK_CREATED",
    )
    return task


@router.get(
    "",
    response_model=list[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieves a paginated list of tasks.",
    response_description="List of tasks retrieved successfully.",
)
def get_all(
    limit: int = Query(10, ge=1, le=100, description="Max number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_all_tasks(
        db, current_user=current_user, limit=limit, offset=offset
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
    description="Retrieves details of a single task using its unique integer ID.",
    response_description="Task details retrieved successfully.",
    responses={404: {"model": ErrorResponse, "description": "Task not found."}},
)
def get_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_task_by_id(task_id, db, current_user=current_user)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Updates title, description, or completion status for an existing task.",
    response_description="Updated task details.",
    responses={
        401: {"description": "Missing or invalid authentication token."},
        404: {"model": ErrorResponse, "description": "Task not found."},
    },
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(task_id, task_in, db, current_user=current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently deletes a task by its unique ID.",
    response_description="Task deleted successfully.",
    responses={
        401: {"description": "Missing or invalid authentication token."},
        404: {"model": ErrorResponse, "description": "Task not found."},
    },
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service.delete_task(task_id, db, current_user=current_user)
