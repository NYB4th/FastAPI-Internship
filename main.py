from fastapi import FastAPI, HTTPException
from routers import task_router, item_router

app = FastAPI()

app.include_router(task_router.router)
app.include_router(item_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastApi internship project"}


@app.get("/health")
def read_health():
    return {"status": "ok"}
