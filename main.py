from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from exceptions.task_exceptions import TaskAlreadyExistsError, TaskNotFoundError
from routers import task_router, item_router
from schemas.error import ErrorResponse

app = FastAPI()

app.include_router(task_router.router)
app.include_router(item_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastApi internship project"}


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    error_payload = ErrorResponse(error_code="TASK_NOT_FOUND", message=exc.message)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_payload.model_dump(),
    )


@app.exception_handler(TaskAlreadyExistsError)
async def task_already_exists_handler(request: Request, exc: TaskAlreadyExistsError):
    error_payload = ErrorResponse(error_code="TASK_DUPLICATE", message=exc.message)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_payload.model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def valtidation_exception_handler(request: Request, exc: RequestValidationError):
    error_payload = ErrorResponse(
        error_code="INVALIDATION_ERROR",
        message="Invalid request body or parameters.",
        details=jsonable_encoder(exc.errors()),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error_payload),
    )


# WHY jsonable_encoder:
# Converts complex Pydantic error objects into JSON-safe Python primitives to prevent serialization crashes (500 Internal Server Error).
