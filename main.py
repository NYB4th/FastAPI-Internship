from fastapi import FastAPI, HTTPException

app = FastAPI()

items_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 25.50},
    {"id": 2, "name": "Mechanical Keyboard", "price": 75.00},
    {"id": 3, "name": "USB-C Monitor", "price": 200.00},
]


@app.get("/")
def read_Root():
    return {"Message": "Welcome to FastApi internship project"}


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/items")
def read_items():
    return {"items": items_db}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="item not found")
