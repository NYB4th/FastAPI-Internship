from exceptions.task_exceptions import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
)
from models.task import Task
from schemas.task import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session

from dependencies.auth import verify_ownership_or_admin
from models.user import User


def get_task_by_id(task_id: int, db: Session, current_user: User):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError(task_id)

    verify_ownership_or_admin(
        task.user_id, current_user  # pyright: ignore[reportArgumentType]
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
    return task


def get_all_tasks(db: Session, current_user: User, limit: int = 10, offset: int = 0):
    query = db.query(Task)
    if current_user.role != "admin":  # pyright: ignore[reportGeneralTypeIssues]
        query = query.filter(Task.user_id == current_user.id)
    return query.offset(offset).limit(limit).all()


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

    return new_task


def delete_task(task_id: int, db: Session, current_user: User):
    task = get_task_by_id(task_id, db, current_user)

    db.delete(task)
    db.commit()
