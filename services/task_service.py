from schemas.task import TaskCreate
from exceptions.task_exceptions import TaskAlreadyExistsError, TaskNotFoundError
from sqlalchemy.orm import Session
from models.task import Task


def get_task_by_id(task_id: int, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError(task_id)
    return task


def get_all_tasks(db: Session):
    return db.query(Task).all()


def create_task(task_in: TaskCreate, db: Session):

    existing_task = (
        db.query(Task).filter(Task.title.ilike(task_in.title.strip())).first()
    )

    if existing_task:
        raise TaskAlreadyExistsError(task_in.title)
    task_data = task_in.model_dump()

    new_task = Task(**task_in.model_dump())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
