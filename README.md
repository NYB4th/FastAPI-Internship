# FastAPI Internship Project - Day 11

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, dependency-driven route authorization, database-backed CRUD operations, database-level query pagination, schema version control using Alembic, asynchronous external API integration with `httpx`, and a fully automated integration testing suite built with Pytest. The system manages PostgreSQL persistent state via SQLAlchemy ORM in production, uses an isolated in-memory SQLite database for test suites, and integrates non-blocking third-party API clients with bounded timeouts and custom domain error handling.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, external API integrations, data persistence, database migrations, and automated testing cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), form data parsing (`OAuth2PasswordRequestForm`), payload parsing, path validation (`post_id >= 1`), and HTTP status codes (`201 Created`, `200 OK`, `204 No Content`, `401 Unauthorized`, `404 Not Found`, `502 Bad Gateway`, `504 Gateway Timeout`, `422 Unprocessable Entity`).
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user`) using `OAuth2PasswordBearer` to extract, decode, and validate incoming Bearer tokens across protected routes.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication (`authenticate_user`), password hashing orchestration, case-insensitive task duplicate checks, in-place ORM updates, deletion transactions, database-level pagination queries, and non-blocking asynchronous HTTP calls (`httpx.AsyncClient`) with bounded 5.0-second timeouts.
- **Utils (`utils/`)**: Enforces security logic such as password hashing and verification using `pwdlib` (with explicit `BcryptHasher`), alongside JWT generation (`create_access_token`) using `PyJWT`.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency.
- **Models (`models/`)**: Defines SQLAlchemy ORM models (`User`, `Task`) representing database tables and column constraints in PostgreSQL.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes (DDL) using Alembic, dynamically bound to `Base.metadata` and environment configuration.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for auth (`UserAlreadyExistsError`), tasks (`TaskNotFoundError`, `TaskAlreadyExistsError`), and upstream external services (`UpstreamNotFoundError`, `UpstreamTimeoutError`, `UpstreamApiError`) for framework-agnostic error translation.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`UserCreate`, `TaskCreate`, `TaskUpdate`), response serialization (`UserResponse`, `PostResponse` with camelCase `alias` mappings), OAuth2 tokens (`Token`, `TokenData`), and error payload contracts (`ErrorResponse`).
- **Global Handlers (`main.py`)**: Registers app startup, routers (`auth`, `task_router`, `item_router`, `external`), and global exception handlers converting domain exceptions into standardized JSON error payloads.
- **Automated Tests (`tests/`)**: Contains modular integration test suites (`test_health.py`, `test_auth.py`, `test_tasks.py`, `test_external.py`) powered by Pytest, `TestClient`, network mocking (`AsyncMock`), and a shared test infrastructure (`conftest.py`) enforcing complete database isolation.

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
│       ├── d6692e76d30b_add_is_completed_to_tasks.py
│       └── e8f2a10b9c3d_create_users_table.py
├── database.py          # SQLAlchemy engine, session factory, and get_db dependency
├── dependencies/
│   ├── __init__.py
│   └── auth.py          # OAuth2PasswordBearer & get_current_user dependency
├── exceptions/
│   ├── __init__.py
│   ├── auth_exceptions.py     # Auth domain exceptions (UserAlreadyExistsError)
│   ├── external_exceptions.py # External domain exceptions (UpstreamNotFoundError, UpstreamTimeoutError, UpstreamApiError)
│   └── task_exceptions.py     # Task domain exceptions
├── main.py              # App initialization, routers & global error handlers
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model
│   └── user.py          # SQLAlchemy ORM user model (users table)
├── pytest.ini           # Pytest runner, testpaths, and coverage configuration
├── README.md            # Architecture, database setup, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, PyJWT, httpx, pytest, pytest-cov, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Token Login)
│   ├── external.py      # HTTP endpoints for /external (JSONPlaceholder integration)
│   ├── item_router.py   # HTTP endpoints for /items
│   └── task_router.py   # HTTP endpoints for /tasks (CRUD, pagination & Auth Protection)
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema
│   ├── external.py      # PostResponse schema with userId alias mapping
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (Create, Update, Read)
│   ├── token.py         # Token & TokenData Pydantic schemas
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse)
├── services/
│   ├── __init__.py
│   ├── external_service.py # Non-blocking HTTP client calls with timeout & exception mapping
│   ├── item_service.py     # Business logic & in-memory item store
│   ├── task_service.py     # Database CRUD operations, pagination & collision checks
│   └── user_service.py     # User creation, authentication & email uniqueness logic
├── tests/               # Automated test suite
│   ├── __init__.py
│   ├── conftest.py      # Shared TestClient & SQLite in-memory DB isolation fixtures
│   ├── test_auth.py     # User registration, duplicate email & token login tests
│   ├── test_external.py # Mocked external API success, timeout & 404 tests
│   ├── test_health.py   # Root (/) and health check (/health) endpoint tests
│   └── test_tasks.py    # Authenticated task CRUD & input validation failure tests
└── utils/
    ├── __init__.py
    └── security.py      # Password hashing (pwdlib) & JWT token utilities (PyJWT)
```

---

## Environment & Security Configuration

Database connection strings and JWT cryptographic secrets are loaded dynamically at runtime via environment variables using `python-dotenv`.

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

## Automated Testing & Test Isolation

The repository includes a fully automated test suite configured with Pytest, `TestClient`, and code coverage reporting (`pytest-cov`).

### Test Isolation Strategy (Protecting Production Data & External Services)

- **In-Memory SQLite Engine:** Database tests execute against an isolated SQLite database held entirely in system memory (`sqlite:///:memory:`). Production PostgreSQL data is completely untouched during test runs.
- **FastAPI Dependency Overrides:** `tests/conftest.py` utilizes `app.dependency_overrides[get_db]` to intercept database session injection across all routers, transparently substituting production database sessions with temporary test sessions.
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

- **`error_code`**: Machine-readable string code (`USER_ALREADY_EXISTS`, `TASK_NOT_FOUND`, `TASK_DUPLICATE`, `INVALIDATION_ERROR`, `UPSTREAM_NOT_FOUND`, `UPSTREAM_TIMEOUT`, `UPSTREAM_ERROR`).
- **`message`**: Human-readable explanation of the error.
- **`details`**: Contextual details (contains field location arrays for 422 validation errors; `null` otherwise).

---

## API Request & Response Examples

### 1. Fetch External Post (`GET /external/posts/{post_id}`)

- **Request:** `GET /external/posts/1`
- **Response (`200 OK`):**

```json
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
}
```

- **Upstream Resource Not Found Response (`404 Not Found`):**

```json
{
  "error_code": "UPSTREAM_NOT_FOUND",
  "message": "The requested external resource was not found.",
  "details": null
}
```

- **Upstream Timeout Response (`504 Gateway Timeout`):**

```json
{
  "error_code": "UPSTREAM_TIMEOUT",
  "message": "The external service request timed out.",
  "details": null
}
```

### 2. Register New User (`POST /auth/register`)

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

### 3. Obtain Access Token (`POST /auth/token`)

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

### 4. Create Task - Protected Endpoint (`POST /tasks`)

- **Header Required:** `Authorization: Bearer <access_token>`
- **Request Body:**

```json
{
  "title": "Complete Async API Integration",
  "description": "Integrate httpx with explicit timeout and error handling",
  "priority": 1
}
```

- **Response (`201 Created`):**

```json
{
  "title": "Complete Async API Integration",
  "description": "Integrate httpx with explicit timeout and error handling",
  "priority": 1,
  "status": "pending",
  "is_completed": false,
  "id": 1
}
```

---

## API Endpoints

| Method   | Endpoint                    | Security           | Layer Handling        | Success          | Error Codes                | Description                                               |
| :------- | :-------------------------- | :----------------- | :-------------------- | :--------------- | :------------------------- | :-------------------------------------------------------- |
| `GET`    | `/`                         | Public             | `main.py`             | `200 OK`         | —                          | Root welcome payload                                      |
| `GET`    | `/health`                   | Public             | `main.py`             | `200 OK`         | —                          | System health check                                       |
| `GET`    | `/external/posts/{post_id}` | Public             | `routers/external.py` | `200 OK`         | `404`, `502`, `504`, `422` | Asynchronous fetch from JSONPlaceholder with 5.0s timeout |
| `POST`   | `/auth/register`            | Public             | `routers/auth.py`     | `201 Created`    | `409`, `422`               | Register user with Bcrypt hashing & unique check          |
| `POST`   | `/auth/token`               | Public (Form Data) | `routers/auth.py`     | `200 OK`         | `401`, `422`               | Verify credentials & return signed JWT token              |
| `GET`    | `/items`                    | Public             | `item_router.py`      | `200 OK`         | —                          | List all items                                            |
| `GET`    | `/items/{item_id}`          | Public             | `item_router.py`      | `200 OK`         | `404`                      | Retrieve item by ID                                       |
| `POST`   | `/tasks`                    | **Bearer Token**   | `task_router.py`      | `201 Created`    | `401`, `409`, `422`        | Protected: Create task for authenticated user             |
| `GET`    | `/tasks`                    | Public             | `task_router.py`      | `200 OK`         | `422`                      | List tasks with `limit` & `offset`                        |
| `GET`    | `/tasks/{task_id}`          | Public             | `task_router.py`      | `200 OK`         | `404`                      | Retrieve task by ID                                       |
| `PUT`    | `/tasks/{task_id}`          | Public             | `task_router.py`      | `200 OK`         | `404`, `409`, `422`        | Update existing task (partial/full)                       |
| `DELETE` | `/tasks/{task_id}`          | Public             | `task_router.py`      | `204 No Content` | `404`                      | Delete task from database                                 |

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
   Ensure `.env` exists in the project root containing `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.

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

Run `pytest` in your terminal. Confirm that all integration tests pass covering root health, user registration, token login, authenticated task creation, fetch-by-ID, input validation bounds (422), and mocked external service integration (200 OK, 404 Not Found, 504 Timeout).

### 2. Manual Verification (Swagger UI)

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify External API Endpoint (`GET /external/posts/{post_id}`):**
   - Expand `GET /external/posts/{post_id}`, click **Try it out**, enter `post_id = 1`, and click **Execute**.
   - Confirm status code is `200 OK` and data returns from JSONPlaceholder.
   - Enter `post_id = 999999` and click **Execute**.
   - Confirm response status code is `404 Not Found` with `UPSTREAM_NOT_FOUND` error code.
3. **Verify Protected Task Endpoint (`POST /tasks`):**
   - Execute without authorization -> Confirm `401 Unauthorized`.
   - Obtain token via `POST /auth/token`, click **Authorize**, submit credentials, and execute `POST /tasks` -> Confirm `201 Created`.

---

## Definition of Done

- [x] Installed `httpx` dependency for non-blocking asynchronous HTTP requests.
- [x] Created `PostResponse` schema in `schemas/external.py` with `alias="userId"` mapping camelCase fields to snake_case.
- [x] Defined custom domain exceptions (`UpstreamNotFoundError`, `UpstreamTimeoutError`, `UpstreamApiError`) in `exceptions/external_exceptions.py`.
- [x] Implemented `get_external_post` service in `services/external_service.py` using `httpx.AsyncClient` with an explicit 5.0-second timeout.
- [x] Implemented `GET /external/posts/{post_id}` route handler in `routers/external.py` with numerical path validation (`post_id >= 1`).
- [x] Registered `external.router` and global exception handlers in `main.py` translating upstream errors to `404`, `504`, and `502` HTTP statuses.
- [x] Created network-isolated tests in `tests/test_external.py` using `AsyncMock` to verify success, 404, and timeout handling without live internet reliance.
- [x] Executed Pytest suite successfully verifying zero regressions across existing authentication and task CRUD tests.
- [x] Updated project documentation and setup instructions in `README.md`.
