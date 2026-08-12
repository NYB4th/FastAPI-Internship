# FastAPI Internship Project - Day 4

A modular, enterprise-structured FastAPI application with a centralized, predictable error-handling layer. The system enforces domain rules at the service layer and transforms failures into a standardized JSON response contract across all HTTP endpoints.

## Architecture Overview

This project uses a layered architecture to keep HTTP handling separate from core data operations:

- **Routers (`routers/`)**: Handles incoming HTTP requests, URL path binding, parameter parsing, and response status codes.
- **Services (`services/`)**: Contains pure Python business logic, state management, and domain validation rules. Raises framework-agnostic Python exceptions.
- **Exceptions (`exceptions/`)**: Defines custom domain exceptions representing business logic failures (e.g., missing records, duplicate data).
- **Schemas (`schemas/`)**: Defines strict Pydantic models for request body validation, response serialization, and a unified error response shape.
- **Global Handlers (`main.py`)**: Intercepts domain exceptions and validation failures at the application root, transforming them into uniform JSON HTTP responses.

## Project Structure

```text
fastapi-internship/
├── .gitignore          # Ignores venv/ and build artifacts
├── exceptions/
│   ├── __init__.py
│   └── task_exceptions.py # Domain-specific Python exceptions
├── main.py             # App initialization, router & global exception registration
├── README.md           # Architecture, error contracts, and setup specs
├── requirements.txt    # Locked dependencies
├── routers/
│   ├── __init__.py
│   ├── item_router.py  # HTTP endpoints for /items
│   └── task_router.py  # HTTP endpoints for /tasks
├── schemas/
│   ├── __init__.py
│   ├── error.py        # Standardized ErrorResponse schema
│   ├── item.py         # Item validation models
│   └── task.py         # Task validation models
└── services/
    ├── __init__.py
    ├── item_service.py # Business logic & in-memory item store
    └── task_service.py # Business logic, duplicate checks & in-memory task store
```

## Standardized Error Contract

All error responses across the API follow a single JSON structure defined in `schemas/error.py`:

```json
{
  "error_code": "STRING_IDENTIFIER",
  "message": "Human-readable explanation of the error.",
  "details": null
}
```

- **`error_code`**: Machine-readable string code (`TASK_NOT_FOUND`, `TASK_DUPLICATE`, `VALIDATION_ERROR`).
- **`message`**: Readable description explaining the failure.
- **`details`**: Optional contextual details (holds Pydantic field validation arrays for 422 errors; `null` for others).

---

## API Failure Response Examples

### 1. Missing Resource (`404 Not Found`)

- **Trigger:** Requesting a non-existent task ID (`GET /tasks/999`).

```json
{
  "error_code": "TASK_NOT_FOUND",
  "message": "Task with ID 999 was not found.",
  "details": null
}
```

### 2. Duplicate Data (`409 Conflict`)

- **Trigger:** Creating a task with a title that already exists (`POST /tasks` with an existing title).

```json
{
  "error_code": "TASK_DUPLICATE",
  "message": "Task with title 'Complete Day 2 Assignment' already exists.",
  "details": null
}
```

### 3. Invalid Request Payload (`422 Unprocessable Entity`)

- **Trigger:** Sending invalid data types or missing required fields (`POST /tasks` with missing `title`).

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid request body or parameters.",
  "details": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## API Endpoints

| Method | Endpoint           | Layer Handling   | Success       | Error Codes  | Description                            |
| :----- | :----------------- | :--------------- | :------------ | :----------- | :------------------------------------- |
| `GET`  | `/`                | `main.py`        | `200 OK`      | —            | Root welcome payload                   |
| `GET`  | `/health`          | `main.py`        | `200 OK`      | —            | System health check                    |
| `GET`  | `/items`           | `item_router.py` | `200 OK`      | —            | List all items via `item_service`      |
| `GET`  | `/items/{item_id}` | `item_router.py` | `200 OK`      | `404`        | Retrieve item by ID via `item_service` |
| `POST` | `/tasks`           | `task_router.py` | `201 Created` | `409`, `422` | Create task with duplicate check       |
| `GET`  | `/tasks`           | `task_router.py` | `200 OK`      | —            | List all tasks via `task_service`      |
| `GET`  | `/tasks/{task_id}` | `task_router.py` | `200 OK`      | `404`        | Retrieve task by ID via `task_service` |

---

## Prerequisites & Setup

1. **Activate virtual environment & run application:**

   ```cmd
   venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

---

## Verification Workflow

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify 404 Handling:**
   - Execute `GET /tasks/999`.
   - Confirm status code is `404 Not Found` and body matches `TASK_NOT_FOUND` schema.
3. **Verify 409 Conflict Handling:**
   - Execute `POST /tasks` with payload `{"title": "Complete Day 2 Assignment", "priority": 1}`.
   - Confirm status code is `409 Conflict` and body matches `TASK_DUPLICATE` schema.
4. **Verify 422 Validation Handling:**
   - Execute `POST /tasks` with payload `{"priority": "invalid_number"}`.
   - Confirm status code is `422 Unprocessable Entity` and `details` contains field location errors.
5. **Verify Happy Path Continuity:**
   - Execute `GET /tasks/1` $\rightarrow$ Returns `200 OK`.
   - Execute `POST /tasks` with a unique title $\rightarrow$ Returns `201 Created`.

---

## Definition of Done

- [x] Standardized `ErrorResponse` model established in `schemas/error.py`.
- [x] Custom Python domain exceptions isolated in `exceptions/task_exceptions.py`.
- [x] Domain validation and exception triggering implemented in `services/task_service.py`.
- [x] Centralized exception handlers registered in `main.py` mapping domain failures to 404, 409, and 422 HTTP responses.
- [x] Router layers cleaned of manual `HTTPException` raises.
- [x] Verification completed across all 3 failure states and happy paths via Interactive Docs.
