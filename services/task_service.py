from schemas.task import TaskCreate, TaskUpdate
from exceptions.task_exceptions import TaskAlreadyExistsError, TaskNotFoundError
from sqlalchemy.orm import Session
from models.task import Task


def get_task_by_id(task_id: int, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError(task_id)
    return task


def update_task(task_id: int, task_in: TaskUpdate, db: Session):
    task = get_task_by_id(task_id, db)

    update_data = task_in.model_dump(exclude_unset=True)
    if "title" in update_data:
        clean_title = update_data["title"].strip()
        existing_task = (
            db.query(Task)
            .filter(Task.title.ilike(clean_title), Task.id != task_id)
            .first()
        )

        if existing_task:
            raise TaskAlreadyExistsError(clean_title)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def get_all_tasks(db: Session, limit: int = 10, offset: int = 0):
    return db.query(Task).offset(offset).limit(limit).all()


def create_task(task_in: TaskCreate, db: Session):

    existing_task = (
        db.query(Task).filter(Task.title.ilike(task_in.title.strip())).first()
    )

    if existing_task:
        raise TaskAlreadyExistsError(task_in.title)

    new_task = Task(**task_in.model_dump())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


def delete_task(task_id: int, db: Session):
    task = get_task_by_id(task_id, db)

    db.delete(task)
    db.commit()
