# FastAPI Internship Project - Day 8

A modular, enterprise-structured FastAPI application featuring secure user registration, database-backed CRUD operations, database-level query pagination, and schema version control using Alembic database migrations. The system manages PostgreSQL persistent state via SQLAlchemy ORM, enforcing strict domain rules, collision checks, input validation bounds, and password security via Bcrypt hashing.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, data persistence, and database migrations cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), payload parsing, and HTTP status codes (`201 Created`, `200 OK`, `204 No Content`). Injects database sessions via `Depends(get_db)`.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, password hashing orchestration, case-insensitive task duplicate checks, in-place ORM updates, deletion transactions, and database-level pagination queries.
- **Utils (`utils/`)**: Enforces security logic such as password hashing and verification using `pwdlib` with explicit `BcryptHasher` configuration.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency.
- **Models (`models/`)**: Defines SQLAlchemy ORM models (`User`, `Task`) representing database tables and column constraints in PostgreSQL.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes (DDL) using Alembic, dynamically bound to `Base.metadata` and environment configuration.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions (`UserAlreadyExistsError`, `TaskNotFoundError`, `TaskAlreadyExistsError`) for framework-agnostic error handling.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`UserCreate`, `TaskCreate`, `TaskUpdate`), response serialization (`UserResponse`, `from_attributes=True`), and error payload contracts (`ErrorResponse`).
- **Global Handlers (`main.py`)**: Registers app startup, routers (`auth`, `task_router`, `item_router`), and global exception handlers for standardized JSON error responses.

---

## Project Structure

```text
fastapi-internship/
├── .env                 # Environment configuration (git-ignored)
├── .env.example         # Environment configuration template
├── .gitignore           # Ignores venv/, .env, and build artifacts
├── alembic.ini          # Alembic CLI configuration file
├── alembic/             # Database migration environment
│   ├── env.py           # Migration execution script with dynamic .env loading
│   ├── README           # Alembic directory description
│   ├── script.py.mako   # Migration script template
│   └── versions/        # Version-controlled migration revision files
│       ├── d6692e76d30b_add_is_completed_to_tasks.py
│       └── e8f2a10b9c3d_create_users_table.py
├── database.py          # SQLAlchemy engine, session factory, and get_db dependency
├── exceptions/
│   ├── __init__.py
│   ├── auth_exceptions.py # Auth domain exceptions (UserAlreadyExistsError)
│   └── task_exceptions.py # Task domain exceptions
├── main.py              # App initialization, routers & global error handlers
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model
│   └── user.py          # SQLAlchemy ORM user model (users table)
├── README.md            # Architecture, database setup, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, pwdlib[bcrypt], Alembic, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (User Registration)
│   ├── item_router.py   # HTTP endpoints for /items
│   └── task_router.py   # HTTP endpoints for /tasks (CRUD & pagination)
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (Create, Update, Read)
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse)
├── services/
│   ├── __init__.py
│   ├── item_service.py  # Business logic & in-memory item store
│   ├── task_service.py  # Database CRUD operations, pagination & collision checks
│   └── user_service.py  # User creation & email uniqueness business logic
└── utils/
    ├── __init__.py
    └── security.py      # Password hashing & verification utilities (pwdlib + Bcrypt)
```

---

## Database Configuration & Migrations

Database connection settings are loaded dynamically at runtime via environment variables using `python-dotenv`.

1. **Environment Setup:**
   Copy `.env.example` to `.env`:

   ```cmd
   copy .env.example .env
   ```

   Set your PostgreSQL connection string inside `.env`:

   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fastapi_db
   ```

2. **Alembic Migration Commands:**
   Alembic handles all database schema changes across environments.
   - **Apply all pending migrations:**
     ```cmd
     alembic upgrade head
     ```
   - **Check current database revision:**
     ```cmd
     alembic current
     ```
   - **Generate a new migration script (autogenerate):**
     ```cmd
     alembic revision --autogenerate -m "description_of_changes"
     ```
   - **Roll back the last applied migration:**
     ```cmd
     alembic downgrade -1
     ```

> **Security Note:** `.env` contains local credentials and is excluded from source control via `.gitignore`. Credentials are dynamically passed into Alembic via `alembic/env.py`.

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

- **`error_code`**: Machine-readable string code (`USER_ALREADY_EXISTS`, `TASK_NOT_FOUND`, `TASK_DUPLICATE`, `INVALIDATION_ERROR`).
- **`message`**: Human-readable explanation of the error.
- **`details`**: Contextual details (contains field location arrays for 422 validation errors; `null` otherwise).

---

## API Request & Response Examples

### 1. Register New User (`POST /auth/register`)

- **Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

- **Response (`201 Created`):**

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

_(Sensitive fields such as raw passwords or `hashed_password` are strictly stripped from responses via `UserResponse` serialization)._

- **Duplicate Email Response (`409 Conflict`):**

```json
{
  "error_code": "USER_ALREADY_EXISTS",
  "message": "User with email 'user@example.com' already exists.",
  "details": null
}
```

### 2. Update Existing Task (`PUT /tasks/1`)

- **Request Body (Partial Update):**

```json
{
  "status": "completed"
}
```

- **Response (`200 OK`):**

```json
{
  "title": "Complete Day 8 Assignment",
  "description": "Implement user registration and password hashing",
  "priority": 1,
  "status": "completed",
  "is_completed": false,
  "id": 1
}
```

### 3. Paginated Task List (`GET /tasks?limit=2&offset=0`)

- **Response (`200 OK`):**

```json
[
  {
    "title": "Task One",
    "description": null,
    "priority": 1,
    "status": "pending",
    "is_completed": false,
    "id": 1
  },
  {
    "title": "Task Two",
    "description": null,
    "priority": 2,
    "status": "pending",
    "is_completed": false,
    "id": 2
  }
]
```

---

## API Endpoints

| Method   | Endpoint           | Layer Handling    | Data Store | Success          | Error Codes         | Description                                      |
| :------- | :----------------- | :---------------- | :--------- | :--------------- | :------------------ | :----------------------------------------------- |
| `GET`    | `/`                | `main.py`         | N/A        | `200 OK`         | —                   | Root welcome payload                             |
| `GET`    | `/health`          | `main.py`         | N/A        | `200 OK`         | —                   | System health check                              |
| `POST`   | `/auth/register`   | `routers/auth.py` | PostgreSQL | `201 Created`    | `409`, `422`        | Register user with Bcrypt hashing & unique check |
| `GET`    | `/items`           | `item_router.py`  | Memory     | `200 OK`         | —                   | List all items                                   |
| `GET`    | `/items/{item_id}` | `item_router.py`  | Memory     | `200 OK`         | `404`               | Retrieve item by ID                              |
| `POST`   | `/tasks`           | `task_router.py`  | PostgreSQL | `201 Created`    | `409`, `422`        | Create task with duplicate title check           |
| `GET`    | `/tasks`           | `task_router.py`  | PostgreSQL | `200 OK`         | `422`               | List tasks with `limit` & `offset`               |
| `GET`    | `/tasks/{task_id}` | `task_router.py`  | PostgreSQL | `200 OK`         | `404`               | Retrieve task by ID                              |
| `PUT`    | `/tasks/{task_id}` | `task_router.py`  | PostgreSQL | `200 OK`         | `404`, `409`, `422` | Update existing task (partial/full)              |
| `DELETE` | `/tasks/{task_id}` | `task_router.py`  | PostgreSQL | `204 No Content` | `404`               | Delete task from database                        |

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

5. **Apply Database Migrations:**

   ```cmd
   alembic upgrade head
   ```

6. **Run Application:**

   ```cmd
   uvicorn main:app --reload
   ```

7. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

---

## Verification Workflow

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Database Revision State:**
   - Run `alembic current` in terminal to confirm database target revision matches `(head)`.
3. **Verify User Registration (`POST /auth/register`):**
   - Send payload `{"email": "user@example.com", "password": "securepassword123"}`.
   - Confirm status `201 Created` returning only `id` and `email`.
   - Re-send exact payload -> Confirm `409 Conflict` with error code `USER_ALREADY_EXISTS`.
   - Send invalid email syntax -> Confirm `422 Unprocessable Entity`.
4. **Verify Task Create & Database Seed (`POST /tasks`):**
   - Execute `POST /tasks` to create multiple tasks.
5. **Verify Update Operations (`PUT /tasks/{id}`):**
   - Execute `PUT /tasks/1` with payload `{"status": "completed"}` -> Confirm status code `200 OK`.
6. **Verify Database Pagination (`GET /tasks`):**
   - Execute `GET /tasks?limit=2&offset=0` -> Returns first 2 tasks.

---

## Definition of Done

- [x] Configured `pwdlib` using explicit `BcryptHasher` for irreversible password hashing.
- [x] Defined `User` SQLAlchemy ORM model with indexed unique `email` and `hashed_password` columns.
- [x] Generated and applied Alembic database migration for `users` table.
- [x] Implemented decoupled Pydantic schemas (`UserCreate`, `UserResponse`) ensuring password fields are never leaked.
- [x] Created `UserAlreadyExistsError` domain exception and registered a global handler in `main.py` mapping to `409 Conflict`.
- [x] Built `services/user_service.py` to handle database persistence, duplicate email checks, and password hashing.
- [x] Implemented `/auth/register` route returning `201 Created` with sanitized JSON response.
- [x] Documented user authentication setup, schemas, endpoints, and verification steps in `README.md`.
