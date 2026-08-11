from fastapi import FastAPI, HTTPException
from routers import task_router
from schmeas.item import ItemRead

app = FastAPI()

app.include_router(task_router.router)

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
