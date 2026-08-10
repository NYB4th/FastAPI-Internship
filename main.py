from fastapi import FastAPI, HTTPException
from typing import Literal
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title can not be empty")
    description: str
    priority: int = Field(
        ..., ge=1, le=5, description="Priority must be between 1 and 5"
    )
    status: Literal["pending", "in_progress", "completed"] = "pending"


class ItemRead(BaseModel):
    id: int = Field(..., gt=0, description="the item must have an id")
    name: str = Field(..., min_length=2, description="the item must have a name")
    price: float = Field(..., gt=0, description="the item must have a price")


class TaskRead(TaskCreate):
    id: int


app = FastAPI()

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

items_db: dict[int, ItemRead] = {
    1: ItemRead(id=1, name="Wireless Mouse", price=25.50),
    2: ItemRead(id=2, name="Mechanical Keyboard", price=75.00),
    3: ItemRead(id=3, name="USB-C Monitor", price=200.00),
}


@app.get("/")
def read_root():
    return {"message": "Welcome to FastApi internship project"}


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get(
    "/items", response_model=list[ItemRead]
)  # list is used when sending multiple dictionary objects
def read_items():
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int):
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task_in: TaskCreate):
    global task_id_counter

    task_data = task_in.model_dump()
    task_data["id"] = task_id_counter

    new_task = TaskRead(**task_data)
    tasks_db[task_id_counter] = new_task

    task_id_counter += 1

    return new_task


@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task
