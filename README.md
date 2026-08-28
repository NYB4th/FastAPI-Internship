# FastAPI Internship Project - Day 15

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, dependency-driven user route authorization, user-scoped relational database CRUD operations with foreign key constraints, database-level query pagination, schema version control using Alembic, centralized environment configuration via `pydantic-settings`, custom request logging middleware with monotonic timing (`time.perf_counter()`) and correlation IDs (`X-Request-ID`), CORS controls, asynchronous external API integration with `httpx`, a fully automated integration testing suite built with Pytest, and comprehensive OpenAPI 3.0 schema metadata with interactive Swagger UI documentation (`/docs`). The system manages PostgreSQL persistent state via SQLAlchemy ORM in production, uses an isolated in-memory SQLite database for test suites, enforces strict resource ownership isolation (`403 Forbidden`), and eliminates code duplication across service layers.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, external API integrations, custom middleware, data persistence, database migrations, interactive documentation, and automated testing cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), form data parsing (`OAuth2PasswordRequestForm`), payload parsing, path validation (`post_id >= 1`), standard response status codes (`201 Created`, `200 OK`, `204 No Content`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `502 Bad Gateway`, `504 Gateway Timeout`, `422 Unprocessable Entity`), and explicit OpenAPI tag declarations. All task operations are strictly protected via user authentication dependencies.
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user`) using `OAuth2PasswordBearer` to extract, decode, and validate incoming Bearer tokens across protected routes, returning the authenticated `User` model context.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication (`authenticate_user`), password hashing orchestration, case-insensitive task duplicate checks per user, user-scoped ORM queries (`Task.user_id == current_user.id`), centralized resource retrieval helpers (`get_task_by_id` reused across update/delete methods to eliminate duplicated lookup logic), database-level pagination, and non-blocking asynchronous HTTP calls (`httpx.AsyncClient`) with bounded 5.0-second timeouts.
- **Utils & Config (`utils/`, `config.py`)**: Manages type-safe application settings via `pydantic-settings` (`Settings`), and enforces security logic such as password hashing and verification using `pwdlib` (with explicit `BcryptHasher`), alongside JWT generation (`create_access_token`) using `PyJWT`.
- **Middleware & Logging (`middleware.py`, `logger.py`)**: Configures standard stdout logging via `logging` (`setup_logger`) and custom HTTP request logging middleware (`RequestLoggingMiddleware`) that intercepts all requests. Captures HTTP method, URL path, HTTP status code, execution duration in milliseconds using monotonic timing (`time.perf_counter()`), and unique request correlation IDs (`X-Request-ID`) while strictly excluding sensitive headers, tokens, credentials, and request/response bodies. Also registers `CORSMiddleware` for cross-origin domain access control.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency driven by application settings.
- **Models (`models/`)**: Defines SQLAlchemy ORM models (`User`, `Task`) representing database tables, column constraints, and foreign key relationships (`user_id = Column(Integer, ForeignKey("users.id"))`) in PostgreSQL.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes (DDL) using Alembic, dynamically bound to `Base.metadata` and environment configuration.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for auth (`UserAlreadyExistsError`), tasks (`TaskNotFoundError`, `TaskAlreadyExistsError`, `TaskForbiddenError`), and upstream external services (`UpstreamNotFoundError`, `UpstreamTimeoutError`, `UpstreamApiError`) for framework-agnostic error translation.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`UserCreate`, `TaskCreate`, `TaskUpdate`), response serialization (`UserResponse`, `TaskRead` including `user_id`, `PostResponse` with camelCase `alias` mappings), OAuth2 tokens (`Token`, `TokenData`), and error payload contracts (`ErrorResponse`). Includes field-level validation bounds, titles, descriptions, and realistic JSON schema examples (`json_schema_extra`).
- **Global Handlers & OpenAPI Metadata (`main.py`)**: Initializes FastAPI with global application metadata (title, description, version, contact information, tag metadata list `openapi_tags`), registers CORS middleware, request logging middleware, router mounting without redundant tag parameters to prevent duplicate entries in Swagger UI, and global exception handlers converting domain exceptions into standardized JSON error payloads.
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
├── logger.py            # Centralized logging configuration using Python standard logging
├── main.py              # App metadata, OpenAPI tag definitions, middleware, clean router inclusion & error handlers
├── middleware.py        # Custom request logging middleware with time.perf_counter() & X-Request-ID
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model with user_id ForeignKey & relationship
│   └── user.py          # SQLAlchemy ORM user model with tasks relationship
├── pytest.ini           # Pytest runner, testpaths, and coverage configuration
├── README.md            # Architecture, database setup, OpenAPI specs, request logging, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, pydantic-settings, PyJWT, httpx, pytest, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Token Login) with tags=["Authentication"]
│   ├── external.py      # HTTP endpoints for /external (JSONPlaceholder integration) with tags=["External Services"]
│   ├── item_router.py   # HTTP endpoints for /items with tags=["Items"]
│   └── task_router.py   # HTTP endpoints for /tasks (User-Scoped CRUD & Auth Protection) with tags=["Tasks"]
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema with OpenAPI field descriptions & examples
│   ├── external.py      # PostResponse schema with userId alias mapping
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (TaskCreate, TaskUpdate, TaskRead with field metadata & examples)
│   ├── token.py         # Token & TokenData Pydantic schemas with OAuth2 field metadata
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse with email validation & field metadata)
├── services/
│   ├── __init__.py
│   ├── external_service.py # Non-blocking HTTP client calls with timeout & exception mapping
│   ├── item_service.py     # Business logic & in-memory item store
│   ├── task_service.py     # User-scoped database CRUD, pagination & refactored reusable get_task_by_id checks
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

## OpenAPI Metadata & Interactive Swagger UI Documentation

The API includes comprehensive OpenAPI 3.0 specifications accessible interactively at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Key Documentation Features

1. **Global API Metadata (`main.py`)**:
   - Explicit application `title`, custom `description`, semantic `version="1.0.0"`, and `contact` maintainer information.
   - Structured `openapi_tags` definitions adding detailed section descriptions to top-level category headers in Swagger UI.
2. **Tag Hierarchy & Disambiguation**:
   - Each endpoint module declares its single authoritative tag within its `APIRouter` declaration (e.g., `tags=["Authentication"]` in `routers/auth.py`, `tags=["Tasks"]` in `routers/task_router.py`, `tags=["External Services"]` in `routers/external.py`).
   - Routers are attached in `main.py` using `app.include_router(router)` without redundant `tags=[...]` parameters. This prevents tag concatenation visual bugs where endpoints appear duplicated across multiple UI headers.
3. **Route Annotations & Documentation**:
   - Every route decorator includes explicit `summary`, `description`, `response_description`, and mapped status code response contracts (`responses={...}`).
4. **Rich Schema Metadata & Examples**:
   - Request and response models utilize `Field()` parameters defining `title`, `description`, `gt`/`ge`/`le` constraints, and concrete `json_schema_extra` example payloads to accelerate API integration.

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

### Adding Trusted CORS Origins

To grant a new frontend client or external domain access to the API:

1. Open `.env` in the project root.
2. Append the new origin URL (including protocol and port, without trailing slash) to the `ALLOWED_ORIGINS` JSON array:

   ```env
   ALLOWED_ORIGINS=["http://localhost:3000","[http://127.0.0.1:8000](http://127.0.0.1:8000)","[https://your-app-domain.com](https://your-app-domain.com)"]
   ```

---

## Request Logging & Observability

The application includes production-friendly request logging middleware (`RequestLoggingMiddleware`) and a centralized logger (`logger.py`) to provide real-time visibility into API performance and endpoint usage.

### Logging Features

- **Monotonic Duration Measurement**: Uses `time.perf_counter()` to calculate total request execution duration accurately in milliseconds without risk of system clock adjustments skewing results.
- **Request Correlation IDs (`X-Request-ID`)**: Reuses an incoming `X-Request-ID` HTTP header or generates a unique UUID4 per request, attaching it to both stdout log entries and outgoing response headers for end-to-end request tracing.
- **Safe Logging Practices**: Captures high-level request metadata (method, URL path, HTTP status code, duration, request ID). Request/response bodies, passwords, tokens, and `Authorization` headers are explicitly excluded to prevent sensitive data exposure.

### Running Application with Logs Enabled

Start the server using Uvicorn:

```cmd
uvicorn main:app --reload
```

### Representative Log Output Examples

- **Successful Request (`200 OK`):**

  ```text
  2026-08-28 00:05:12,345 - fastapi_app - INFO - [8a0519fd-e987-4de5-8366-af626b47fc51] GET /health Status: 200 - Duration: 1.45ms
  ```

- **Error Response (`404 Not Found`):**
  ```text
  2026-08-28 00:05:20,112 - fastapi_app - INFO - [f8e7d6c5-b4a3-2109-dcba-0987654321ba] GET /tasks/999999 Status: 404 - Duration: 3.82ms
  ```

### Troubleshooting Example

Consider the following production log line generated during operation:

```text
2026-08-28 00:10:45,892 - fastapi_app - INFO - [c9bf9e57-1685-4c89-bafb-ff5af830be8a] GET /external/posts/1 Status: 504 - Duration: 5004.12ms
```

**Field-by-Field Diagnostic Analysis:**

1. **`[c9bf9e57-1685-4c89-bafb-ff5af830be8a]` (Correlation ID)**: Uniquely identifies this specific HTTP transaction. A developer can copy this ID from a client report or header and search log monitoring tools (e.g., Datadog, CloudWatch) to isolate all events associated with this single call.
2. **`GET /external/posts/1` (Method & Path)**: Pinpoints the specific endpoint invoked by the client.
3. **`Status: 504` (HTTP Status Code)**: Indicates a `504 Gateway Timeout`, confirming the issue was caused by an upstream service failure rather than an internal application crash or syntax error.
4. **`Duration: 5004.12ms` (Elapsed Duration)**: Highlights that the execution time reached the 5.0-second timeout limit set in `httpx.AsyncClient`. This immediately proves latency was due to third-party network unresponsiveness rather than local database or server resource starvation.

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

| Method   | Endpoint                    | Tag Category      | Security           | Success          | Error Codes                | Description                                                |
| :------- | :-------------------------- | :---------------- | :----------------- | :--------------- | :------------------------- | :--------------------------------------------------------- |
| `GET`    | `/`                         | Health            | Public             | `200 OK`         | —                          | Root welcome message payload                               |
| `GET`    | `/health`                   | Health            | Public             | `200 OK`         | —                          | System availability and health check                       |
| `POST`   | `/auth/register`            | Authentication    | Public             | `201 Created`    | `409`, `422`               | Register user account with password hashing                |
| `POST`   | `/auth/token`               | Authentication    | Public (Form Data) | `200 OK`         | `401`, `422`               | Authenticate credentials and issue OAuth2 Bearer JWT token |
| `POST`   | `/tasks`                    | Tasks             | **Bearer Token**   | `201 Created`    | `401`, `409`, `422`        | Create a new task assigned to the authenticated user       |
| `GET`    | `/tasks`                    | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `422`               | Retrieve a paginated list of user tasks                    |
| `GET`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `403`, `404`        | Retrieve details of a single task by ID                    |
| `PUT`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `403`, `404`, `409` | Update details or completion status of an existing task    |
| `DELETE` | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `204 No Content` | `401`, `403`, `404`        | Permanently delete a task by ID                            |
| `GET`    | `/items`                    | Items             | Public             | `200 OK`         | —                          | Retrieve list of items                                     |
| `GET`    | `/items/{item_id}`          | Items             | Public             | `200 OK`         | `404`                      | Retrieve single item by ID                                 |
| `GET`    | `/external/posts/{post_id}` | External Services | Public             | `200 OK`         | `404`, `502`, `504`, `422` | Asynchronously fetch external post with 5s timeout         |

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
   Navigate to `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc`

---

## Verification Workflow via Swagger UI & Pytest

### 1. Automated Verification (CLI)

Run `pytest` in your terminal. Confirm that all integration tests pass covering root health, user registration, token login, user-scoped task creation, resource isolation across multiple users (`403 Forbidden`), fetch-by-ID, input validation bounds (422), and mocked external service integration (200 OK, 404 Not Found, 504 Timeout).

### 2. Manual Verification (Swagger UI)

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Interactive OpenAPI Metadata & Category Headers:**
   - Confirm title, description, contact details, and version reflect application metadata.
   - Verify category descriptions under `Health`, `Authentication`, `Tasks`, `Items`, and `External Services`.
   - Confirm no duplicate endpoint listings or duplicate tag categories exist.
3. **Verify Protected Task Authorization & Ownership (`POST /tasks`, `GET /tasks`):**
   - Execute `GET /tasks` without authorization -> Confirm `401 Unauthorized`.
   - Register User A (`POST /auth/register`), obtain token via `POST /auth/token`, click **Authorize**, and submit `POST /tasks`. Confirm `201 Created` with `user_id = 1`.
   - Register User B (`POST /auth/register`), obtain User B's token, and attempt `GET /tasks/1` (User A's task). Confirm `403 Forbidden` with `TASK_FORBIDDEN` error code.

---

## Definition of Done

- [x] Configured global application metadata, contact information, and tag metadata descriptions in `main.py`.
- [x] Standardized router tags across `auth.py`, `task_router.py`, `item_router.py`, and `external.py` to prevent duplicate tag headers in Swagger UI.
- [x] Added detailed endpoint `summary`, `description`, `response_description`, and response status code dictionaries across all API routes.
- [x] Enriched Pydantic schemas with field descriptions, titles, validation constraints, and concrete `json_schema_extra` example payloads.
- [x] Refactored `task_service.py` to reuse `get_task_by_id` inside `update_task` and `delete_task`, eliminating redundant database lookup code.
- [x] Maintained 100% test suite pass rate with Pytest covering authenticated task CRUD, authorization constraints, logging, and mocked external APIs.
- [x] Updated project documentation to accurately reflect OpenAPI metadata enhancements and refactored architecture.
