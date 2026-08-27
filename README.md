# FastAPI Internship Project - Day 12

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, dependency-driven user route authorization, user-scoped relational database CRUD operations with foreign key constraints, database-level query pagination, schema version control using Alembic, centralized environment configuration via `pydantic-settings`, custom middleware for request timing and CORS controls, asynchronous external API integration with `httpx`, and a fully automated integration testing suite built with Pytest. The system manages PostgreSQL persistent state via SQLAlchemy ORM in production, uses an isolated in-memory SQLite database for test suites, and enforces strict resource ownership isolation (`403 Forbidden`) across all user-created resources.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, external API integrations, custom middleware, data persistence, database migrations, and automated testing cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), form data parsing (`OAuth2PasswordRequestForm`), payload parsing, path validation (`post_id >= 1`), and HTTP status codes (`201 Created`, `200 OK`, `204 No Content`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `502 Bad Gateway`, `504 Gateway Timeout`, `422 Unprocessable Entity`). All task operations are strictly protected via user authentication dependencies.
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user`) using `OAuth2PasswordBearer` to extract, decode, and validate incoming Bearer tokens across protected routes, returning the authenticated `User` model context.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication (`authenticate_user`), password hashing orchestration, case-insensitive task duplicate checks per user, user-scoped ORM queries (`Task.user_id == current_user.id`), in-place ORM updates, deletion transactions, database-level pagination, and non-blocking asynchronous HTTP calls (`httpx.AsyncClient`) with bounded 5.0-second timeouts.
- **Utils & Config (`utils/`, `config.py`)**: Manages type-safe application settings via `pydantic-settings` (`Settings`), and enforces security logic such as password hashing and verification using `pwdlib` (with explicit `BcryptHasher`), alongside JWT generation (`create_access_token`) using `PyJWT`.
- **Middleware (`middleware/`)**: Provides request instrumentation through custom HTTP middleware (`RequestLoggingMiddleware`) for tracing request execution durations (`X-Process-Time` header) and registers `CORSMiddleware` for cross-origin domain access control.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency driven by application settings.
- **Models (`models/`)**: Defines SQLAlchemy ORM models (`User`, `Task`) representing database tables, column constraints, and foreign key relationships (`user_id = Column(Integer, ForeignKey("users.id"))`) in PostgreSQL.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes (DDL) using Alembic, dynamically bound to `Base.metadata` and environment configuration.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for auth (`UserAlreadyExistsError`), tasks (`TaskNotFoundError`, `TaskAlreadyExistsError`, `TaskForbiddenError`), and upstream external services (`UpstreamNotFoundError`, `UpstreamTimeoutError`, `UpstreamApiError`) for framework-agnostic error translation.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`UserCreate`, `TaskCreate`, `TaskUpdate`), response serialization (`UserResponse`, `TaskResponse` including `user_id`, `PostResponse` with camelCase `alias` mappings), OAuth2 tokens (`Token`, `TokenData`), and error payload contracts (`ErrorResponse`).
- **Global Handlers (`main.py`)**: Registers app startup, CORS middleware, request logging middleware, routers (`auth`, `task_router`, `item_router`, `external`), and global exception handlers converting domain exceptions into standardized JSON error payloads.
- **Automated Tests (`tests/`)**: Contains modular integration test suites (`test_health.py`, `test_auth.py`, `test_tasks.py`, `test_external.py`) powered by Pytest, `TestClient`, network mocking (`AsyncMock`), and a shared test infrastructure (`conftest.py`) enforcing complete database isolation and multi-user access security checks.

---

## Project Structure

```text
fastapi-internship/
├── .env                 # Environment configuration & security secrets (git-ignored)
├── .env.example         # Environment configuration template
├── .gitignore           # Ignores venv/, .env, and build artifacts
├── alembic.ini          # Alembic CLI configuration file
├── alembic/             # Database migration environment
│   ├── env.py           # Migration execution script with dynamic .env loading
│   ├── README           # Alembic directory description
│   ├── script.py.mako   # Migration script template
│   └── versions/        # Version-controlled migration revision files
│       ├── a9f3b82c10d4_add_user_id_to_tasks.py
│       ├── d6692e76d30b_add_is_completed_to_tasks.py
│       └── e8f2a10b9c3d_create_users_table.py
├── config.py            # Type-safe environment settings via pydantic-settings
├── database.py          # SQLAlchemy engine, session factory, and get_db dependency
├── dependencies/
│   ├── __init__.py
│   └── auth.py          # OAuth2PasswordBearer & get_current_user dependency
├── exceptions/
│   ├── __init__.py
│   ├── auth_exceptions.py     # Auth domain exceptions (UserAlreadyExistsError)
│   ├── external_exceptions.py # External domain exceptions (UpstreamNotFoundError, UpstreamTimeoutError, UpstreamApiError)
│   └── task_exceptions.py     # Task domain exceptions (TaskNotFoundError, TaskForbiddenError, etc.)
├── main.py              # App initialization, CORS, middleware, routers & error handlers
├── middleware/
│   ├── __init__.py
│   └── logging.py       # Custom request processing time & execution logging middleware
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model with user_id ForeignKey & relationship
│   └── user.py          # SQLAlchemy ORM user model with tasks relationship
├── pytest.ini           # Pytest runner, testpaths, and coverage configuration
├── README.md            # Architecture, database setup, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, pydantic-settings, PyJWT, httpx, pytest, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Token Login)
│   ├── external.py      # HTTP endpoints for /external (JSONPlaceholder integration)
│   ├── item_router.py   # HTTP endpoints for /items
│   └── task_router.py   # HTTP endpoints for /tasks (User-Scoped CRUD & Auth Protection)
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema
│   ├── external.py      # PostResponse schema with userId alias mapping
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (Create, Update, Read with user_id)
│   ├── token.py         # Token & TokenData Pydantic schemas
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse)
├── services/
│   ├── __init__.py
│   ├── external_service.py # Non-blocking HTTP client calls with timeout & exception mapping
│   ├── item_service.py     # Business logic & in-memory item store
│   ├── task_service.py     # User-scoped database CRUD, pagination & ownership validation
│   └── user_service.py     # User creation, authentication & email uniqueness logic
├── tests/               # Automated test suite
│   ├── __init__.py
│   ├── conftest.py      # Shared TestClient & SQLite in-memory DB isolation fixtures
│   ├── test_auth.py     # User registration, duplicate email & token login tests
│   ├── test_external.py # Mocked external API success, timeout & 404 tests
│   ├── test_health.py   # Root (/) and health check (/health) endpoint tests
│   └── test_tasks.py    # Authenticated user-scoped task CRUD & 403 forbidden tests
└── utils/
    ├── __init__.py
    └── security.py      # Password hashing (pwdlib) & JWT token utilities (PyJWT)
```

---

## Environment & Security Configuration

Database connection strings, CORS origins, and cryptographic secrets are loaded dynamically at runtime using `pydantic-settings` from the environment `.env` file via `config.py`.

1. **Environment Setup:**
   Copy `.env.example` to `.env`:

   ```cmd
   copy .env.example .env
   ```

   Configure your `.env` variables:

   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fastapi_db
   SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ALLOWED_ORIGINS=["http://localhost:3000","[http://127.0.0.1:8000](http://127.0.0.1:8000)"]
   ```

2. **Alembic Migration Commands:**
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

> **Security Note:** `.env` contains local secrets and database credentials and is excluded from source control via `.gitignore`. Never commit raw `SECRET_KEY` values to public repositories.

---

## Automated Testing & Multi-User Test Isolation

The repository includes a fully automated test suite configured with Pytest, `TestClient`, and code coverage reporting (`pytest-cov`).

### Test Isolation & Multi-User Security Strategy

- **In-Memory SQLite Engine:** Database tests execute against an isolated SQLite database held entirely in system memory (`sqlite:///:memory:`). Production PostgreSQL data is completely untouched during test runs.
- **FastAPI Dependency Overrides:** `tests/conftest.py` utilizes `app.dependency_overrides[get_db]` to intercept database session injection across all routers, transparently substituting production database sessions with temporary test sessions.
- **Multi-User Access & Ownership Tests:** `tests/test_tasks.py` initializes distinct test users (`user1`, `user2`) with separate access tokens. Tests explicitly verify that `User A` cannot read, modify, or delete tasks belonging to `User B`, ensuring proper enforcement of `403 Forbidden` (`TASK_FORBIDDEN`) domain constraints.
- **Network Isolation via Mocking:** `tests/test_external.py` uses `unittest.mock.patch` and `AsyncMock` to intercept calls to `get_external_post`. Tests simulate upstream 200 OK responses, 404 Not Found errors, and 504 Timeouts locally without relying on live third-party network availability.
- **Per-Test Schema Lifecycle:** The `db_session` Pytest fixture executes `Base.metadata.create_all()` before each individual test runs and invokes `Base.metadata.drop_all()` immediately after completion, guaranteeing 100% test independence without leftover data side effects.

### Executing the Test Suite

Run all automated tests and generate a line-by-line coverage report:

```cmd
pytest
```

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

- **`error_code`**: Machine-readable string code (`USER_ALREADY_EXISTS`, `TASK_NOT_FOUND`, `TASK_DUPLICATE`, `TASK_FORBIDDEN`, `INVALIDATION_ERROR`, `UPSTREAM_NOT_FOUND`, `UPSTREAM_TIMEOUT`, `UPSTREAM_ERROR`).
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

### 2. Obtain Access Token (`POST /auth/token`)

- **Request Body (`application/x-www-form-urlencoded`):**

```text
username=user@example.com&password=securepassword123
```

- **Response (`200 OK`):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create Task - Protected & User-Scoped (`POST /tasks`)

- **Header Required:** `Authorization: Bearer <access_token>`
- **Request Body:**

```json
{
  "title": "Enforce Task Ownership",
  "description": "Relate tasks to authenticated user_id via Foreign Key",
  "priority": 1
}
```

- **Response (`201 Created`):**

```json
{
  "title": "Enforce Task Ownership",
  "description": "Relate tasks to authenticated user_id via Foreign Key",
  "priority": 1,
  "status": "pending",
  "is_completed": false,
  "id": 1,
  "user_id": 1
}
```

### 4. Cross-User Resource Access Forbidden (`GET /tasks/{task_id}`)

- **Header Required:** `Authorization: Bearer <user_2_access_token>` (Attempting to access Task 1 owned by User 1)
- **Response (`403 Forbidden`):**

```json
{
  "error_code": "TASK_FORBIDDEN",
  "message": "You do not have permission to access or modify this task.",
  "details": null
}
```

---

## API Endpoints

| Method   | Endpoint                    | Security           | Layer Handling        | Success          | Error Codes                | Description                                                |
| :------- | :-------------------------- | :----------------- | :-------------------- | :--------------- | :------------------------- | :--------------------------------------------------------- |
| `GET`    | `/`                         | Public             | `main.py`             | `200 OK`         | —                          | Root welcome payload                                       |
| `GET`    | `/health`                   | Public             | `main.py`             | `200 OK`         | —                          | System health check                                        |
| `GET`    | `/external/posts/{post_id}` | Public             | `routers/external.py` | `200 OK`         | `404`, `502`, `504`, `422` | Asynchronous fetch from JSONPlaceholder with 5.0s timeout  |
| `POST`   | `/auth/register`            | Public             | `routers/auth.py`     | `201 Created`    | `409`, `422`               | Register user with Bcrypt hashing & unique check           |
| `POST`   | `/auth/token`               | Public (Form Data) | `routers/auth.py`     | `200 OK`         | `401`, `422`               | Verify credentials & return signed JWT token               |
| `GET`    | `/items`                    | Public             | `item_router.py`      | `200 OK`         | —                          | List all items                                             |
| `GET`    | `/items/{item_id}`          | Public             | `item_router.py`      | `200 OK`         | `404`                      | Retrieve item by ID                                        |
| `POST`   | `/tasks`                    | **Bearer Token**   | `task_router.py`      | `201 Created`    | `401`, `409`, `422`        | Protected: Create task bound to authenticated `user_id`    |
| `GET`    | `/tasks`                    | **Bearer Token**   | `task_router.py`      | `200 OK`         | `401`, `422`               | Protected: List authenticated user's tasks with pagination |
| `GET`    | `/tasks/{task_id}`          | **Bearer Token**   | `task_router.py`      | `200 OK`         | `401`, `403`, `404`        | Protected: Retrieve authenticated user's task by ID        |
| `PUT`    | `/tasks/{task_id}`          | **Bearer Token**   | `task_router.py`      | `200 OK`         | `401`, `403`, `404`, `409` | Protected: Update authenticated user's task (partial/full) |
| `DELETE` | `/tasks/{task_id}`          | **Bearer Token**   | `task_router.py`      | `204 No Content` | `401`, `403`, `404`        | Protected: Delete authenticated user's task from database  |

---

## Prerequisites & Setup

1. **Prerequisites:**
   - Python 3.10+
   - PostgreSQL installed and running locally.

2. **Install Dependencies:**

   ```cmd
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Ensure `.env` exists in the project root containing `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `ALLOWED_ORIGINS`.

4. **Apply Database Migrations:**

   ```cmd
   alembic upgrade head
   ```

5. **Run Application:**

   ```cmd
   uvicorn main:app --reload
   ```

6. **Run Automated Tests:**

   ```cmd
   pytest
   ```

7. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

---

## Verification Workflow via Swagger UI & Pytest

### 1. Automated Verification (CLI)

Run `pytest` in your terminal. Confirm that all integration tests pass covering root health, user registration, token login, user-scoped task creation, resource isolation across multiple users (`403 Forbidden`), fetch-by-ID, input validation bounds (422), and mocked external service integration (200 OK, 404 Not Found, 504 Timeout).

### 2. Manual Verification (Swagger UI)

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Environment Settings & Middleware Headers:**
   - Submit any request and inspect response headers to confirm `X-Process-Time` measurement header is returned.
3. **Verify Protected Task Authorization & Ownership (`POST /tasks`, `GET /tasks`):**
   - Execute `GET /tasks` without authorization -> Confirm `401 Unauthorized`.
   - Register User A (`POST /auth/register`), obtain token via `POST /auth/token`, click **Authorize**, and submit `POST /tasks`. Confirm `201 Created` with `user_id = 1`.
   - Register User B (`POST /auth/register`), obtain User B's token, and attempt `GET /tasks/1` (User A's task). Confirm `403 Forbidden` with `TASK_FORBIDDEN` error code.

---

## Definition of Done

- [x] Defined `user_id` foreign key relationship between `User` and `Task` ORM models.
- [x] Created and applied Alembic migration `a9f3b82c10d4_add_user_id_to_tasks.py` enforcing database foreign key constraints.
- [x] Refactored environment configuration management to use `pydantic-settings` (`Settings` class in `config.py`).
- [x] Implemented custom `TaskForbiddenError` and mapped it to a standardized `403 Forbidden` error payload.
- [x] Secured all `/tasks` endpoints (`GET`, `POST`, `PUT`, `DELETE`) with `get_current_user` dependency for ownership-based authorization.
- [x] Configured `CORSMiddleware` and custom `RequestLoggingMiddleware` for request execution timing (`X-Process-Time`) and tracing headers.
- [x] Refactored `task_service.py` to scope all database queries and mutations by `user_id`.
- [x] Updated Pydantic `TaskResponse` schema to include `user_id` output fields.
- [x] Extended Pytest suite in `tests/test_tasks.py` with multi-user isolation tests verifying `403 Forbidden` enforcement on unauthorized cross-user modifications.
- [x] Passed 100% of integration tests with full test isolation on an SQLite in-memory database.
