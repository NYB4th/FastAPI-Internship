# FastAPI Internship Project - Day 3

A modular, enterprise-structured FastAPI application demonstrating separation of concerns through dedicated Pydantic schemas, isolated service logic, and modular API routers for both `Task` and `Item` resources.

## Architecture Overview

This project uses a layered architecture to keep HTTP handling separate from core data operations:

- **Routers (`routers/`)**: Handles incoming HTTP requests, URL path binding, parameter parsing, response status codes, and HTTP exceptions (`404 Not Found`).
- **Services (`services/`)**: Contains pure Python business logic, state management, and in-memory data access. Completely independent of web frameworks.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for request body validation and response serialization.

## Project Structure

```text
fastapi-internship/
├── .gitignore          # Ignores venv/ and build artifacts
├── main.py             # App initialization and router registration
├── README.md           # Architecture, setup, and API specifications
├── requirements.txt    # Locked dependencies
├── routers/
│   ├── __init__.py
│   ├── item_router.py  # HTTP endpoints for /items
│   └── task_router.py  # HTTP endpoints for /tasks
├── schemas/
│   ├── __init__.py
│   ├── item.py         # Item validation models
│   └── task.py         # Task validation models
└── services/
    ├── __init__.py
    ├── item_service.py # Business logic & in-memory item store
    └── task_service.py # Business logic & in-memory task store
```

## Prerequisites & Setup

1. **Activate virtual environment & run application:**

   ```cmd
   venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint           | Layer Handling   | Status Code           | Description                            |
| :----- | :----------------- | :--------------- | :-------------------- | :------------------------------------- |
| `GET`  | `/`                | `main.py`        | `200 OK`              | Root welcome payload                   |
| `GET`  | `/health`          | `main.py`        | `200 OK`              | System health check                    |
| `GET`  | `/items`           | `item_router.py` | `200 OK`              | List all items via `item_service`      |
| `GET`  | `/items/{item_id}` | `item_router.py` | `200 OK` / `404`      | Retrieve item by ID via `item_service` |
| `POST` | `/tasks`           | `task_router.py` | `201 Created` / `422` | Create task via `task_service`         |
| `GET`  | `/tasks`           | `task_router.py` | `200 OK`              | List all tasks via `task_service`      |
| `GET`  | `/tasks/{task_id}` | `task_router.py` | `200 OK` / `404`      | Retrieve task by ID via `task_service` |

## Verification Workflow

1. Open `http://127.0.0.1:8000/docs`.
2. **Items Endpoint Testing:**
   - Test `GET /items` $\rightarrow$ Verify HTTP `200 OK` returning item array.
   - Test `GET /items/1` $\rightarrow$ Verify HTTP `200 OK` returning item payload.
   - Test `GET /items/999` $\rightarrow$ Verify HTTP `404 Not Found`.
3. **Tasks Endpoint Testing:**
   - Test `POST /tasks` with valid payload $\rightarrow$ Verify HTTP `201 Created` response.
   - Test `GET /tasks` $\rightarrow$ Verify newly created task is returned in JSON list.
   - Test `GET /tasks/{task_id}` with existing ID $\rightarrow$ Verify HTTP `200 OK`.
   - Test `GET /tasks/999` with non-existent ID $\rightarrow$ Verify HTTP `404 Not Found`.

## Definition of Done

- [x] Task and Item endpoints decoupled into `routers/task_router.py` and `routers/item_router.py`.
- [x] In-memory storage and data access isolated in `services/task_service.py` and `services/item_service.py`.
- [x] Pydantic models structured cleanly inside `schemas/task.py` and `schemas/item.py`.
- [x] Both routers registered in `main.py` via `app.include_router()`.
- [x] HTTP status codes properly assigned across all routes (`201 Created`, `200 OK`, `404 Not Found`).
