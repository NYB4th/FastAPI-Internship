# FastAPI Internship Project - Day 6

A modular, enterprise-structured FastAPI application featuring full database-backed CRUD operations for tasks and database-level query pagination. The system manages PostgreSQL persistent state via SQLAlchemy ORM, enforcing strict domain rules, collision checks, partial field updates, and input validation bounds.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, data persistence, and schemas cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), and HTTP status codes. Injects database sessions via `Depends(get_db)`.
- **Services (`services/`)**: Implements core business logic, case-insensitive duplicate checks, in-place ORM updates, deletion transactions, and database-level pagination queries.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency.
- **Models (`models/`)**: Defines SQLAlchemy ORM models representing database tables and column constraints in PostgreSQL.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for framework-agnostic error handling.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`TaskCreate`, `TaskUpdate`), response serialization (`from_attributes=True`), and error payload contracts.
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
│   └── task_router.py  # HTTP endpoints for /tasks (CRUD & pagination)
├── schemas/
│   ├── __init__.py
│   ├── error.py        # Standardized ErrorResponse schema
│   ├── item.py         # Item validation models
│   └── task.py         # Task Pydantic schemas (Create, Update, Read)
└── services/
    ├── __init__.py
    ├── item_service.py # Business logic & in-memory item store
    └── task_service.py # Database CRUD operations, pagination & collision checks
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

## API Request & Response Examples

### 1. Update Existing Task (`PUT /tasks/1`)

- **Request Body (Partial Update):**

```json
{
  "status": "completed"
}
```

- **Response (`200 OK`):**

```json
{
  "title": "Complete Day 6 Assignment",
  "description": "Implement CRUD and pagination",
  "priority": 1,
  "status": "completed",
  "id": 1
}
```

### 2. Delete Task (`DELETE /tasks/1`)

- **Response (`204 No Content`):** Empty body.

### 3. Paginated Task List (`GET /tasks?limit=2&offset=0`)

- **Response (`200 OK`):**

```json
[
  {
    "title": "Task One",
    "description": null,
    "priority": 1,
    "status": "pending",
    "id": 1
  },
  {
    "title": "Task Two",
    "description": null,
    "priority": 2,
    "status": "pending",
    "id": 2
  }
]
```

---

## API Endpoints

| Method   | Endpoint           | Layer Handling   | Data Store | Success          | Error Codes         | Description                            |
| :------- | :----------------- | :--------------- | :--------- | :--------------- | :------------------ | :------------------------------------- |
| `GET`    | `/`                | `main.py`        | N/A        | `200 OK`         | —                   | Root welcome payload                   |
| `GET`    | `/health`          | `main.py`        | N/A        | `200 OK`         | —                   | System health check                    |
| `GET`    | `/items`           | `item_router.py` | Memory     | `200 OK`         | —                   | List all items                         |
| `GET`    | `/items/{item_id}` | `item_router.py` | Memory     | `200 OK`         | `404`               | Retrieve item by ID                    |
| `POST`   | `/tasks`           | `task_router.py` | PostgreSQL | `201 Created`    | `409`, `422`        | Create task with duplicate title check |
| `GET`    | `/tasks`           | `task_router.py` | PostgreSQL | `200 OK`         | `422`               | List tasks with `limit` & `offset`     |
| `GET`    | `/tasks/{task_id}` | `task_router.py` | PostgreSQL | `200 OK`         | `404`               | Retrieve task by ID                    |
| `PUT`    | `/tasks/{task_id}` | `task_router.py` | PostgreSQL | `200 OK`         | `404`, `409`, `422` | Update existing task (partial/full)    |
| `DELETE` | `/tasks/{task_id}` | `task_router.py` | PostgreSQL | `204 No Content` | `404`               | Delete task from database              |

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

## Verification Workflow

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Create & Database Seed:**
   - Execute `POST /tasks` to create multiple tasks.
3. **Verify Update Operations (`PUT /tasks/{id}`):**
   - Execute `PUT /tasks/1` with payload `{"status": "completed"}`.
   - Confirm status code `200 OK` and verify only `status` changed while other fields remain preserved.
   - Execute `PUT /tasks/1` with an existing title of another task. Confirm `409 Conflict`.
4. **Verify Database Pagination (`GET /tasks`):**
   - Execute `GET /tasks?limit=2&offset=0` $\rightarrow$ Returns first 2 tasks.
   - Execute `GET /tasks?limit=2&offset=2` $\rightarrow$ Returns next slice of tasks.
   - Execute `GET /tasks?limit=-1` $\rightarrow$ Confirm `422 Unprocessable Entity`.
5. **Verify Delete Operations (`DELETE /tasks/{id}`):**
   - Execute `DELETE /tasks/1` $\rightarrow$ Confirm `204 No Content`.
   - Execute `GET /tasks/1` $\rightarrow$ Confirm `404 Not Found`.

---

## Definition of Done

- [x] Defined `TaskUpdate` schema with optional fields in `schemas/task.py`.
- [x] Implemented database-backed `update_task` service using `exclude_unset=True` for partial updates and title collision checks.
- [x] Implemented database-backed `delete_task` service with `204 No Content` HTTP response.
- [x] Added validated `limit` and `offset` query parameters (`Query`) to `GET /tasks` executed directly via SQL `.offset().limit()`.
- [x] Enforced uniform `404 Not Found` error responses for missing record updates and deletions.
- [x] Verified full CRUD and paginated list behavior against PostgreSQL.
