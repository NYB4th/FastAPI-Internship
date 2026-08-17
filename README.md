# FastAPI Internship Project - Day 5

A modular, enterprise-structured FastAPI application with centralized error handling, PostgreSQL database persistence, and SQLAlchemy ORM integration. The system uses FastAPI dependency injection to manage per-request database sessions and enforces business logic rules over durable database storage.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, data persistence, and schemas cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, and status codes. Injects per-request database sessions via `Depends(get_db)`.
- **Services (`services/`)**: Implements core business logic and queries PostgreSQL using SQLAlchemy ORM models.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency.
- **Models (`models/`)**: Defines SQLAlchemy ORM models representing database tables and column constraints in PostgreSQL.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for framework-agnostic error handling.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation, response serialization (`from_attributes=True`), and error payload contracts.
- **Global Handlers (`main.py`)**: Registers app startup table creation, routers, and global exception handlers for standardized JSON error responses.

---

## Project Structure

```text
fastapi-internship/
├── .env                # Environment configuration (git-ignored)
├── .env.example        # Environment configuration template
├── .gitignore          # Ignores venv/, .env, and build artifacts
├── database.py         # SQLAlchemy engine, session factory, and get_db dependency
├── exceptions/
│   ├── __init__.py
│   └── task_exceptions.py # Custom domain exceptions
├── main.py             # App initialization, table auto-creation, routers & error handlers
├── models/
│   ├── __init__.py
│   └── task.py         # SQLAlchemy ORM task model (PostgreSQL tasks table)
├── README.md           # Architecture, database setup, and API specifications
├── requirements.txt    # Application dependencies
├── routers/
│   ├── __init__.py
│   ├── item_router.py  # HTTP endpoints for /items
│   └── task_router.py  # HTTP endpoints for /tasks (injected with DB session)
├── schemas/
│   ├── __init__.py
│   ├── error.py        # Standardized ErrorResponse schema
│   ├── item.py         # Item validation models
│   └── task.py         # Task Pydantic schemas (with ORM mode enabled)
└── services/
    ├── __init__.py
    ├── item_service.py # Business logic & in-memory item store
    └── task_service.py # Database operations & case-insensitive duplicate checks
```

---

## Database Configuration

Database configuration is loaded at runtime via environment variables using `python-dotenv`.

1. Copy `.env.example` to `.env`:
   ```cmd
   copy .env.example .env
   ```
2. Set your PostgreSQL connection string inside `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fastapi_db
   ```

> **Security Note:** `.env` contains local credentials and is excluded from source control via `.gitignore`.

---

## Standardized Error Contract

All error responses across the API follow a uniform JSON contract defined in `schemas/error.py`:

```json
{
  "error_code": "STRING_IDENTIFIER",
  "message": "Human-readable explanation of the error.",
  "details": null
}
```

- **`error_code`**: Machine-readable string code (`TASK_NOT_FOUND`, `TASK_DUPLICATE`, `INVALIDATION_ERROR`).
- **`message`**: Human-readable explanation of the error.
- **`details`**: Contextual details (contains field location arrays for 422 errors; `null` otherwise).

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

- **Trigger:** Creating a task with a title that already exists in PostgreSQL (`POST /tasks`).

```json
{
  "error_code": "TASK_DUPLICATE",
  "message": "Task with title 'Complete Day 5' already exists.",
  "details": null
}
```

### 3. Invalid Request Payload (`422 Unprocessable Entity`)

- **Trigger:** Sending invalid data types or missing required fields.

```json
{
  "error_code": "INVALIDATION_ERROR",
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

| Method | Endpoint           | Layer Handling   | Data Store | Success       | Error Codes  | Description                       |
| :----- | :----------------- | :--------------- | :--------- | :------------ | :----------- | :-------------------------------- |
| `GET`  | `/`                | `main.py`        | N/A        | `200 OK`      | —            | Root welcome payload              |
| `GET`  | `/health`          | `main.py`        | N/A        | `200 OK`      | —            | System health check               |
| `GET`  | `/items`           | `item_router.py` | Memory     | `200 OK`      | —            | List all items                    |
| `GET`  | `/items/{item_id}` | `item_router.py` | Memory     | `200 OK`      | `404`        | Retrieve item by ID               |
| `POST` | `/tasks`           | `task_router.py` | PostgreSQL | `201 Created` | `409`, `422` | Create task with database persist |
| `GET`  | `/tasks`           | `task_router.py` | PostgreSQL | `200 OK`      | —            | List all tasks from database      |
| `GET`  | `/tasks/{task_id}` | `task_router.py` | PostgreSQL | `200 OK`      | `404`        | Retrieve task from database by ID |

---

## Prerequisites & Setup

1. **Prerequisites:**
   - Python 3.10+
   - PostgreSQL installed and running locally.

2. **Create Database:**
   Open `psql` or pgAdmin and run:

   ```sql
   CREATE DATABASE fastapi_db;
   ```

3. **Install Dependencies:**

   ```cmd
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Ensure `.env` exists in the project root with a valid `DATABASE_URL`.

5. **Run Application:**

   ```cmd
   uvicorn main:app --reload
   ```

6. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

---

## Verification Workflow (Proof of Persistence)

1. Open `http://127.0.0.1:8000/docs`.
2. **Create a Persistent Task:**
   - Execute `POST /tasks` with body:
     ```json
     {
       "title": "Verify PostgreSQL Persistence",
       "description": "Checking durability across server restarts",
       "priority": 1,
       "status": "pending"
     }
     ```
   - Confirm response code `201 Created` and note the returned `id` (e.g., `id: 1`).
3. **Restart API Server:**
   - Press `Ctrl + C` in the terminal to terminate Uvicorn.
   - Restart the server: `uvicorn main:app --reload`.
4. **Verify Data Retention:**
   - Execute `GET /tasks/1`.
   - Confirm status code `200 OK` and verify the exact record created prior to restart is returned from PostgreSQL.

---

## Definition of Done

- [x] Environment variable configuration established with `.env` and `.env.example`.
- [x] Database connection pool and dependency session generator configured in `database.py`.
- [x] SQLAlchemy ORM `Task` model created in `models/task.py`.
- [x] Automatic database table generation enabled in `main.py`.
- [x] Task routers and service refactored to execute transactions via injected `Session` dependencies.
- [x] Pydantic `TaskRead` schema updated with `from_attributes=True` for ORM compatibility.
- [x] Data persistence verified across application process restarts.
