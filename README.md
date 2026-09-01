# FastAPI Internship Project - Day 17

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, dependency-driven route authorization, relational database CRUD operations, database-level query pagination, schema version control using Alembic, centralized environment configuration via `pydantic-settings`, custom request logging middleware with monotonic timing (`time.perf_counter()`) and correlation IDs (`X-Request-ID`), CORS controls, asynchronous external API integration with `httpx`, a fully automated integration testing suite built with Pytest, and comprehensive OpenAPI 3.0 schema metadata with interactive Swagger UI documentation (`/docs`).

---

## Architecture Overview & Request Flow

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, custom middleware, data persistence, and automated testing cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, path validation, and standard response status codes.
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user`) using `OAuth2PasswordBearer` to validate incoming Bearer tokens.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication, task duplicate checks, and pagination.
- **Utils & Config (`utils/`, `config.py`)**: Manages environment settings via `pydantic-settings` (`Settings`) and security logic (password hashing via `pwdlib` and JWT generation via `PyJWT`).
- **Middleware & Logging (`middleware.py`, `logger.py`)**: Configures custom request logging middleware (`RequestLoggingMiddleware`) capturing execution duration with `time.perf_counter()` and `X-Request-ID` correlation headers, alongside CORS controls.
- **Database & Models (`database.py`, `models/`)**: Configures the SQLAlchemy database engine, session factory, and ORM models (`User`, `Task`) representing PostgreSQL tables.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes using Alembic.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for auth and tasks for framework-agnostic error translation.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for request validation and response serialization.
- **Automated Tests (`tests/`)**: Modular integration test suites powered by Pytest, `TestClient`, and SQLite in-memory isolation.

### End-to-End HTTP Request Flow

When a client sends a request (e.g., `POST /tasks`), it passes through these layers sequentially:

```text
[Client HTTP Request]
       │
       ▼
 1. RequestLoggingMiddleware  ──► Assigns X-Request-ID & starts execution timer
       │
       ▼
 2. CORSMiddleware            ──► Validates request origin against ALLOWED_CORS_ORIGINS
       │
       ▼
 3. Router Layer (routers/)   ──► Matches path /tasks, parses body via Pydantic schema
       │
       ▼
 4. Dependency (auth.py)      ──► Extracts & validates Bearer token to get User context
       │
       ▼
 5. Service Layer (services/) ──► Executes business logic & checks database constraints
       │
       ▼
 6. Database Layer (models/)  ──► SQLAlchemy ORM executes SQL statements via get_db session
       │
       ▼
 7. Response Handler          ──► Formats result into JSON schema & returns HTTP 201 Created
```

---

## Project Structure

```text
fastapi-internship/
├── .env                 # Environment configuration & security secrets (git-ignored)
├── .env.example         # Environment configuration template
├── .gitignore           # Ignores venv/, .env, build artifacts, and test caches
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
│   └── task_exceptions.py     # Task domain exceptions (TaskNotFoundError, TaskAlreadyExistsError)
├── logger.py            # Centralized logging configuration using Python standard logging
├── main.py              # App metadata, OpenAPI tag definitions, middleware, clean router inclusion & error handlers
├── middleware.py        # Custom request logging middleware with time.perf_counter() & X-Request-ID
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model
│   └── user.py          # SQLAlchemy ORM user model
├── pytest.ini           # Pytest runner, testpaths, and coverage configuration
├── README.md            # Architecture, database setup, OpenAPI specs, request logging, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, pydantic-settings, PyJWT, httpx, pytest, pytest-cov, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Token Login) with tags=["Authentication"]
│   ├── external.py      # HTTP endpoints for /external (JSONPlaceholder integration) with tags=["External Services"]
│   ├── item_router.py   # HTTP endpoints for /items with tags=["Items"]
│   └── task_router.py   # HTTP endpoints for /tasks (CRUD & Auth Protection) with tags=["Tasks"]
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
│   ├── task_service.py     # Database CRUD, pagination, None-safe updates & refactored reusable get_task_by_id checks
│   └── user_service.py     # User creation, authentication & email uniqueness logic
├── tests/               # Automated test suite
│   ├── __init__.py
│   ├── conftest.py      # Shared TestClient & SQLite in-memory DB isolation fixtures
│   ├── test_auth.py     # User registration, duplicate email & token login tests
│   ├── test_config_cors.py # CORS configuration tests
│   ├── test_external.py # Mocked external API success, timeout & 404 tests
│   ├── test_health.py   # Root (/) and health check (/health) endpoint tests
│   └── test_tasks.py    # Complete registration-to-task workflow, pagination, duplicate check & 401 unauthenticated tests
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
   - Each endpoint module declares its single authoritative tag within its `APIRouter` declaration (`tags=["Authentication"]`, `tags=["Tasks"]`, `tags=["External Services"]`).
   - Routers are attached in `main.py` using `app.include_router(router)` without redundant `tags=[...]` parameters to prevent tag duplication bugs in Swagger UI.
3. **Route Annotations & Documentation**:
   - Every route decorator includes explicit `summary`, `description`, `response_description`, and mapped status code response contracts (`responses={...}`).
4. **Rich Schema Metadata & Examples**:
   - Request and response models utilize `Field()` parameters defining `title`, `description`, `gt`/`ge`/`le` constraints, and concrete `json_schema_extra` example payloads.

---

## Environment & Security Configuration

Database connection strings, CORS origins, and cryptographic secrets are loaded dynamically at runtime using `pydantic-settings` from `.env` via `config.py`.

1. **Environment Setup:**
   Copy `.env.example` to `.env`:

   ```cmd
   copy .env.example .env
   ```

   Configure your `.env` variables:

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   SECRET_KEY=your_super_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=development
   ALLOWED_CORS_ORIGINS=["http://localhost:3000","[http://127.0.0.1:3000](http://127.0.0.1:3000)"]
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

### Adding Trusted CORS Origins

To grant a new frontend client or external domain access to the API:

1. Open `.env` in the project root.
2. Append the new origin URL (including protocol and port, without trailing slash) to the `ALLOWED_CORS_ORIGINS` JSON array:

   ```env
   ALLOWED_CORS_ORIGINS=["http://localhost:3000","[http://127.0.0.1:3000](http://127.0.0.1:3000)","[https://your-app-domain.com](https://your-app-domain.com)"]
   ```

---

## Prerequisites & Setup Guide

### 1. Prerequisites

- Python 3.10+
- PostgreSQL database running locally

### 2. Environment Setup

Activate your virtual environment and install dependencies:

```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

Create your local environment file by copying the template:

```cmd
copy .env.example .env
```

_Note: Update `.env` with your local PostgreSQL password and secret keys._

### 3. Database Migrations

Run Alembic migrations to build required database tables (`users`, `tasks`):

```cmd
alembic upgrade head
```

Verify current migration revision status:

```cmd
alembic current
```

### 4. Application Startup

Start the FastAPI server using Uvicorn:

```cmd
uvicorn main:app --reload
```

The interactive Swagger API documentation will be available at `http://127.0.0.1:8000/docs`.

### 5. Execute Automated Tests

Run the integration test suite using the isolated in-memory SQLite database:

```cmd
pytest -v --cov
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

---

### Representative Log Output Examples

- **Successful Request (`200 OK`):**

  ```text
  2026-08-28 00:05:12,345 - fastapi_app - INFO - [8a0519fd-e987-4de5-8366-af626b47fc51] GET /health Status: 200 - Duration: 1.45ms
  ```

- **Error Response (`404 Not Found`):**
  ```text
  2026-08-28 00:05:20,112 - fastapi_app - INFO - [f8e7d6c5-b4a3-2109-dcba-0987654321ba] GET /tasks/999999 Status: 404 - Duration: 3.82ms
  ```

---

## Automated Testing & Integration Workflow Isolation

The repository includes a fully automated test suite configured with Pytest, `TestClient`, and code coverage reporting (`pytest-cov`).

### Test Isolation & Registration-to-Task Workflow Strategy

- **In-Memory SQLite Engine:** Database tests execute against an isolated SQLite database held entirely in system memory (`sqlite:///:memory:`). Production PostgreSQL data is completely untouched during test runs.
- **FastAPI Dependency Overrides:** `tests/conftest.py` utilizes `app.dependency_overrides[get_db]` to intercept database session injection across all routers, transparently substituting production database sessions with temporary test sessions.
- **End-to-End Registration-to-Task Workflow:** `test_complete_task_lifecycle` in `tests/test_tasks.py` exercises the complete workflow: registering a user, logging in to obtain an access token, creating a task, retrieving it, updating it, deleting it, and verifying 404 cleanup.
- **Unauthenticated Protection & Duplicate Handling:** Integration tests explicitly verify that accessing task endpoints without a Bearer token returns `401 Unauthorized`, and creating a task with a duplicate title returns `409 Conflict`.
- **Network Isolation via Mocking:** `tests/test_external.py` uses `unittest.mock.patch` and `AsyncMock` to intercept calls to `get_external_post`. Tests simulate upstream 200 OK responses, 404 Not Found errors, and 504 Timeouts locally without relying on live third-party network availability.
- **Per-Test Schema Lifecycle:** The `db_session` Pytest fixture executes `Base.metadata.create_all()` before each individual test runs and invokes `Base.metadata.drop_all()` immediately after completion, guaranteeing 100% test independence without leftover data side effects.

### Executing the Test Suite

Run all automated tests with verbose output and coverage reporting:

```cmd
pytest -v --cov
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

## Core API Request & Response Examples

### 1. System Health Check (`GET /health`)

- **Headers:** None
- **Request Body:** None
- **Response (`200 OK`):**

```json
{
  "status": "healthy"
}
```

### 2. User Registration (`POST /auth/register`)

- **Headers:** `Content-Type: application/json`
- **Request Body (JSON):**

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

- **Headers:** `Content-Type: application/x-www-form-urlencoded`
- **Request Body (Form Data):**

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

### 4. Create Protected Task (`POST /tasks`)

- **Headers:**
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
  "title": "Complete Day 17 Handover",
  "description": "Document API architecture and setup workflow",
  "priority": 1
}
```

- **Response (`201 Created`):**

```json
{
  "id": 1,
  "title": "Complete Day 17 Handover",
  "description": "Document API architecture and setup workflow",
  "priority": 1,
  "status": "pending",
  "is_completed": false
}
```

---

## Live Technical Demo Script

Follow this 5-step sequence in Swagger UI (`http://127.0.0.1:8000/docs`) to demonstrate the end-to-end user workflow:

1. **Verify System Health (`GET /health`)**
   - **Action:** Click "Try it out" and execute `GET /health`.
   - **Expected Output:** Status `200 OK` with `{"status": "healthy"}`.
   - **Talking Point:** Proves the application server is up, running, and accepting HTTP requests.

2. **Register a User Account (`POST /auth/register`)**
   - **Action:** Submit JSON body with `email` and `password`.
   - **Expected Output:** Status `201 Created` with the new user `id` and `email`.
   - **Talking Point:** Shows account creation where passwords are encrypted using Bcrypt before saving to PostgreSQL.

3. **Authenticate & Obtain Token (`POST /auth/token`)**
   - **Action:** Enter email into `username` and password into `password` (form-data format) and execute.
   - **Expected Output:** Status `200 OK` returning a signed JWT `access_token`.
   - **Talking Point:** Demonstrates OAuth2 password flow issuing short-lived access tokens.

4. **Authorize Swagger UI Session**
   - **Action:** Copy the `access_token` string, click the **Authorize** lock button at the top of Swagger UI, paste the token, and authorize.
   - **Talking Point:** Attaches the Bearer token header to all subsequent requests across the documentation page.

5. **Create Protected Task (`POST /tasks`)**
   - **Action:** Submit task JSON body containing `title`, `description`, and `priority`.
   - **Expected Output:** Status `201 Created` with the created task details.
   - **Talking Point:** Demonstrates protected route authorization where the `get_current_user` dependency decodes the token and permits task creation.

---

## Verification Workflow via Swagger UI & Pytest

### 1. Automated Verification (CLI)

Run `pytest -v --cov` in your terminal. Confirm that all integration tests pass covering root health, user registration, token login, complete task CRUD lifecycle, duplicate title conflict handling (409), pagination, unauthenticated route protection (401), input validation bounds (422), and mocked external service integration (200 OK, 404 Not Found, 504 Timeout).

### 2. Manual Verification (Swagger UI)

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Interactive OpenAPI Metadata & Category Headers:**
   - Confirm title, description, contact details, and version reflect application metadata.
   - Verify category descriptions under `Health`, `Authentication`, `Tasks`, `Items`, and `External Services`.
   - Confirm no duplicate endpoint listings or duplicate tag categories exist.
3. **Verify Protected Task Authorization (`POST /tasks`, `GET /tasks`):**
   - Execute `GET /tasks` without authorization -> Confirm `401 Unauthorized`.
   - Register a user (`POST /auth/register`), obtain token via `POST /auth/token`, click **Authorize**, and submit `POST /tasks`. Confirm `201 Created`.
   - Send duplicate `POST /tasks` with identical title -> Confirm `409 Conflict`.

---

## API Endpoints

| Method   | Endpoint                    | Tag Category      | Security           | Success          | Error Codes                | Description                                                |
| :------- | :-------------------------- | :---------------- | :----------------- | :--------------- | :------------------------- | :--------------------------------------------------------- |
| `GET`    | `/`                         | Health            | Public             | `200 OK`         | —                          | Root welcome message payload                               |
| `GET`    | `/health`                   | Health            | Public             | `200 OK`         | —                          | System availability and health check                       |
| `POST`   | `/auth/register`            | Authentication    | Public             | `201 Created`    | `409`, `422`               | Register user account with password hashing                |
| `POST`   | `/auth/token`               | Authentication    | Public (Form Data) | `200 OK`         | `401`, `422`               | Authenticate credentials and issue OAuth2 Bearer JWT token |
| `POST`   | `/tasks`                    | Tasks             | **Bearer Token**   | `201 Created`    | `401`, `409`, `422`        | Create a new task                                          |
| `GET`    | `/tasks`                    | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `422`               | Retrieve a paginated list of tasks                         |
| `GET`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `404`               | Retrieve details of a single task by ID                    |
| `PUT`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `200 OK`         | `401`, `404`, `409`, `422` | Update details or completion status of an existing task    |
| `DELETE` | `/tasks/{task_id}`          | Tasks             | **Bearer Token**   | `204 No Content` | `401`, `404`               | Permanently delete a task by ID                            |
| `GET`    | `/items`                    | Items             | Public             | `200 OK`         | —                          | Retrieve list of items                                     |
| `GET`    | `/items/{item_id}`          | Items             | Public             | `200 OK`         | `404`                      | Retrieve single item by ID                                 |
| `GET`    | `/external/posts/{post_id}` | External Services | Public             | `200 OK`         | `404`, `502`, `504`, `422` | Asynchronously fetch external post with 5s timeout         |

---

## Remaining Issues Checklist

### Unresolved Issues & Cleanup

- [ ] **Fix and standardize the Items module:** The current focus was on getting the Tasks module working, so Items still uses basic in-memory dictionaries. Refactor it to use PostgreSQL, SQLAlchemy models, Alembic migrations, JWT authentication (`get_current_user`), and the same standardized error format used elsewhere in the project.

- [ ] **Make all files consistent:** The Tasks domain already has proper logging, validation, custom exceptions, and integration tests, but the Items and External modules do not fully follow the same standard. Review the project files and bring these modules up to a more consistent level.

### Future Enhancements & Practice

- [ ] **Give tasks a proper purpose & user isolation:** Add a `user_id` foreign key to the `Task` model so users only see and manage their own tasks instead of sharing tasks globally. Add more realistic fields such as due dates and priority levels.

- [ ] **Attempt frontend integration:** Practice backend integration with an existing frontend application instead of relying only on Swagger UI for testing the API.

- [ ] **Apply industry-standard techniques:** Add practical improvements such as simple rate limiting on login and registration routes to help block repetitive or abusive requests.

---

## Definition of Done

- [x] Verified the full registration-to-authenticated-task workflow through the automated integration test suite.
- [x] Verified database isolation using the in-memory SQLite test database and FastAPI dependency overrides.
- [x] Verified authentication, protected task routes, pagination, duplicate title conflict handling (409), and unauthenticated protection (401).
- [x] Verified mocked external service integration covering success, 404 Not Found, and 504 Timeout scenarios.
- [x] Verified OpenAPI metadata, Swagger UI documentation, request logging, correlation IDs, and CORS configuration.
- [x] Updated `README.md` to reflect the current Day 17 architecture, setup workflow, API examples, verification workflow, and project status.

---

## Project Retrospective & Future Improvements

### 1. Significant Technical Challenge

During integration testing, database state from earlier tests persisted into subsequent runs. This caused intermittent failures such as duplicate email errors during registration tests (`409 Conflict`) and unexpected task pagination counts.

### 2. Resolution Strategy

Configured `tests/conftest.py` to use an isolated in-memory SQLite database (`sqlite:///:memory:`). Created a `db_session` Pytest fixture that executes `Base.metadata.create_all()` before each test and `Base.metadata.drop_all()` immediately after completion. Connected this fixture to FastAPI using `app.dependency_overrides[get_db]`.

### 3. Key Learning Outcome

Gained practical experience with FastAPI's `app.dependency_overrides` feature. It allowed us to swap the production PostgreSQL database connection with an isolated test session dynamically without modifying any core application logic in `routers/` or `services/`.

### 4. Actionable Future Improvement

Add explicit user ownership to tasks by defining a `user_id` foreign key on the `Task` ORM model. Currently, any authenticated user can view or modify tasks created by other users. Adding `user_id` filtering will enforce true multi-tenant data isolation per user account.
