class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task with ID {task_id} was not found"
        super().__init__(self.message)


class TaskAlreadyExistsError(Exception):
    def __init__(self, title: str):
        self.title = title
        self.message = f"Task with title '{title}' already exists."
        super().__init__(self.message)
