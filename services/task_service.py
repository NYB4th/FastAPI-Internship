from schmeas.task import TaskCreate, TaskRead
from exceptions.task_exceptions import TaskAlreadyExistsError, TaskNotFoundError

tasks_db: dict[int, TaskRead] = {
    1: TaskRead(
        id=1,
        title="Complete Day 2 Assignment",
        description="Implement Pydantic validation models",
        priority=1,
        status="completed",
    )
}
task_id_counter = 2


def get_task_by_id(task_id: int):
    task = tasks_db.get(task_id)
    if not task:
        raise TaskNotFoundError(task_id)
    return task


def get_all_tasks():
    return list(tasks_db.values())


def create_task(task_in: TaskCreate):
    global task_id_counter

    for existing_task in tasks_db.values():
        if existing_task.title.strip().lower() == task_in.title.strip().lower():
            raise TaskAlreadyExistsError(task_in.title)

    task_data = task_in.model_dump()

    task_data["id"] = task_id_counter

    new_task = TaskRead(**task_data)
    tasks_db[task_id_counter] = new_task

    task_id_counter += 1

    return new_task
