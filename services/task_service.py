from exceptions.task_exceptions import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
)
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskRead
from sqlalchemy.orm import Session

from dependencies.auth import verify_ownership_or_admin
from models.user import User

from services.cache_service import get_cache, set_cache, delete_cache_pattern
from typing import cast


def invalidate_task_caches(user_id: int) -> None:
    delete_cache_pattern(f"tasks:user:{user_id}:*")
    delete_cache_pattern("tasks:admin:*")


def get_task_by_id(task_id: int, db: Session, current_user: User):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError(task_id)

    user_id = cast(int, task.user_id)
    verify_ownership_or_admin(
        user_id,
        current_user,
    )
    return task


def update_task(task_id: int, task_in: TaskUpdate, db: Session, current_user: User):
    task = get_task_by_id(task_id, db, current_user)

    update_data = task_in.model_dump(exclude_unset=True)
    if "title" in update_data and update_data["title"] is not None:
        clean_title = update_data["title"].strip()
        existing_task = (
            db.query(Task)
            .filter(
                Task.title.ilike(clean_title),
                Task.id != task_id,
                Task.user_id == task.user_id,
            )
            .first()
        )

        if existing_task:
            raise TaskAlreadyExistsError(clean_title)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    invalidate_task_caches(task.user_id)  # pyright: ignore[reportArgumentType]
    return task


def get_all_tasks(db: Session, current_user: User, limit: int = 10, offset: int = 0):
    if current_user.role == "admin":  # pyright: ignore[reportGeneralTypeIssues]
        cache_key = f"tasks:admin:limit:{limit}:offset:{offset}"
    else:
        cache_key = f"tasks:user:{current_user.id}:limit:{limit}:offset:{offset}"

    cached_data = get_cache(cache_key)
    if cached_data is not None:
        return [TaskRead.model_validate(item) for item in cached_data]

    query = db.query(Task)
    if current_user.role != "admin":  # pyright: ignore[reportGeneralTypeIssues]
        query = query.filter(Task.user_id == current_user.id)
    db_tasks = query.offset(offset).limit(limit).all()

    tasks_read = [TaskRead.model_validate(task) for task in db_tasks]
    cache_payload = [task.model_dump(mode="json") for task in tasks_read]
    set_cache(cache_key, cache_payload)

    return tasks_read


def create_task(task_in: TaskCreate, db: Session, user_id: int):
    clean_title = task_in.title.strip()
    existing_task = (
        db.query(Task)
        .filter(Task.title.ilike(clean_title), Task.user_id == user_id)
        .first()
    )

    if existing_task:
        raise TaskAlreadyExistsError(clean_title)

    new_task = Task(**task_in.model_dump(), user_id=user_id)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    invalidate_task_caches(user_id)
    return new_task


def delete_task(task_id: int, db: Session, current_user: User):
    task = get_task_by_id(task_id, db, current_user)
    owner_id = task.user_id

    db.delete(task)
    db.commit()

    invalidate_task_caches(owner_id)  # pyright: ignore[reportArgumentType]
