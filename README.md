# FastAPI Internship Project - Day 20

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, role-based and resource-ownership route authorization, relational database CRUD operations, database-level query pagination, Redis-backed cache-aside behavior with reliable mutation invalidation, IP-based authentication rate limiting, schema version control using Alembic, centralized environment configuration via `pydantic-settings`, custom request logging middleware with monotonic timing (`time.perf_counter()`) and correlation IDs (`X-Request-ID`), CORS controls, asynchronous external API integration with `httpx`, a fully automated integration testing suite built with Pytest, and comprehensive OpenAPI 3.0 schema metadata with interactive Swagger UI documentation (`/docs`).

---

## Architecture Overview & Request Flow

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, custom middleware, data persistence, and automated testing cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, path validation, and standard response status codes.
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user` and `require_admin`) using `OAuth2PasswordBearer` and client rate limiting (`rate_limit_login`).
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication, task ownership filtering, pagination, resilient Redis caching (`cache_service.py`), and background audit logging (`audit.py`).
- **Utils & Config (`utils/`, `config.py`)**: Manages environment settings via `pydantic-settings` (`Settings`) and security logic (password hashing via `pwdlib` and JWT generation via `PyJWT`).
- **Middleware & Logging (`middleware.py`, `logger.py`)**: Configures custom request logging middleware (`RequestLoggingMiddleware`) capturing execution duration with `time.perf_counter()` and `X-Request-ID` correlation headers, alongside CORS controls.
- **Database & Models (`database.py`, `models/`)**: Configures the SQLAlchemy database engine, session factory, and ORM models (`User`, `Task`) representing PostgreSQL tables.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes using Alembic.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions for auth, tasks, and external services for framework-agnostic error translation.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for request validation and response serialization.
- **Automated Tests (`tests/`)**: Modular integration test suites powered by Pytest, `TestClient`, SQLite in-memory isolation, and automated Redis cache lifecycle fixtures.

### End-to-End HTTP Request Flow

When a client sends a request (e.g., `GET /tasks` or `POST /auth/token`), it passes through these layers sequentially:

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
  3. Router Layer (routers/)   ──► Matches path, parses parameters via Pydantic schemas
         │
         ▼
  4. Dependency Layer          ──► Extracts JWT / checks roles / applies Redis rate limiter
         │
         ▼
  5. Service Layer (services/) ──► Checks Redis cache first (Cache-Aside)
         │                            │
         ├──────── [Cache Hit] ───────┘ (Returns cached JSON without DB access)
         ▼
  6. Database Layer (models/)  ──► SQLAlchemy executes SQL query on PostgreSQL via Session
         │
         ▼
  7. Cache Population          ──► Serializes result & populates Redis with short TTL
         │
         ▼
  8. Response Handler          ──► Formats result into JSON schema & returns HTTP response
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
│       ├── 037764b3457e_add_role_to_users_and_user_id_to_tasks.py
│       ├── 0fce7b76d432_create_users_table.py
│       └── d6692e76d30b_add_is_completed_to_tasks.py
├── config.py            # Type-safe environment settings via pydantic-settings
├── database.py          # SQLAlchemy engine, session factory, and get_db dependency
├── dependencies/
│   ├── __init__.py
│   ├── auth.py          # OAuth2PasswordBearer, get_current_user & require_admin dependencies
│   └── rate_limiter.py  # Redis-backed atomic IP rate limiting dependency
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
│   ├── task.py          # SQLAlchemy ORM task model with user ownership relationship
│   └── user.py          # SQLAlchemy ORM user model with role field
├── pytest.ini           # Pytest runner, testpaths, and coverage configuration
├── README.md            # Architecture, database setup, caching docs, API specs, and retrospective
├── requirements.txt     # Application dependencies (FastAPI, pydantic-settings, PyJWT, redis, httpx, pytest, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Rate-Limited Token Login)
│   ├── external.py      # HTTP endpoints for /external (JSONPlaceholder integration)
│   ├── item_router.py   # HTTP endpoints for /items with tags=["Items"]
│   ├── task_router.py   # HTTP endpoints for /tasks (CRUD, Background Tasks, Auth Protection)
│   └── user_router.py   # HTTP endpoints for /users (Role Management)
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema with OpenAPI field descriptions & examples
│   ├── external.py      # PostResponse schema with userId alias mapping
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (TaskCreate, TaskUpdate, TaskRead with user_id)
│   ├── token.py         # Token & TokenData Pydantic schemas with OAuth2 field metadata
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse, UserRoleUpdate)
├── services/
│   ├── __init__.py
│   ├── audit.py            # Asynchronous audit event logging executed post-commit
│   ├── cache_service.py    # Resilient Redis cache client with graceful error handling & TTL support
│   ├── external_service.py # Non-blocking HTTP client calls with timeout & exception mapping
│   ├── item_service.py     # Business logic & in-memory item store
│   ├── task_service.py     # Database CRUD, cache-aside read logic, and mutation-based cache invalidation
│   └── user_service.py     # User creation, authentication & email uniqueness logic
├── tests/               # Automated test suite
│   ├── __init__.py
│   ├── conftest.py      # Shared TestClient, SQLite DB isolation & Redis flush fixtures
│   ├── test_auth.py     # User registration, default role, token login & rate limiting tests
│   ├── test_config_cors.py # CORS configuration tests
│   ├── test_external.py # Mocked external API success, timeout & 404 tests
│   ├── test_health.py   # Root (/) and health check (/health) endpoint tests
│   └── test_tasks.py    # Task lifecycle, RBAC, ownership, cache miss/hit, TTL & invalidation tests
└── utils/
    ├── __init__.py
    └── security.py      # Password hashing (pwdlib) & JWT token utilities (PyJWT)
```

---

## Redis Caching Architecture & Cache-Aside Flow

The application implements the **Cache-Aside (Lazy Loading)** pattern for task listings (`GET /tasks`) to minimize repetitive database load and deliver fast repeated reads.

### 1. The Cache-Aside Lifecycle

```text
[GET /tasks Request]
         │
         ▼
[Construct Cache Key] ──► tasks:user:{user_id}:limit:{limit}:offset:{offset}
         │
         ▼
 [Check Redis Cache]
         │
    ┌────┴──────────────────────────┐
    ▼                               ▼
[Cache Hit]                    [Cache Miss]
    │                               │
    │ (Deserializes JSON)           ▼
    │                       [Query PostgreSQL DB]
    │                               │
    │                       [Serialize with TaskRead]
    │                               │
    │                       [Write to Redis with TTL=60s]
    │                               │
    └──────────────┬────────────────┘
                   ▼
        [Return 200 OK Response]
```

1. **Cache Hit:** The endpoint constructs a scoped key. If the key exists in Redis, the serialized JSON list is decoded into Pydantic `TaskRead` instances and PostgreSQL query execution is bypassed.
2. **Cache Miss:** If the key is absent or expired, the database is queried, results are serialized via `TaskRead`, stored in Redis with an automatic expiration time (TTL), and returned to the client.

### 2. Cache Key Strategy & Isolation

Cache keys are structured to guarantee strict user-level data isolation and prevent query parameter collisions:

| Role / Scope | Key Pattern                                          | Description                                        |
| :----------- | :--------------------------------------------------- | :------------------------------------------------- |
| Regular User | `tasks:user:{user_id}:limit:{limit}:offset:{offset}` | Caches paginated lists strictly owned by `user_id` |
| Admin User   | `tasks:admin:limit:{limit}:offset:{offset}`          | Caches global administrative paginated task lists  |

### 3. Reliable Cache Invalidation on Mutations

To prevent stale data from misleading clients, any operation that mutates task state automatically purges matching cache keys immediately after the transaction is committed (`db.commit()`):

- **Task Creation (`POST /tasks`):** Calls `invalidate_task_caches(user_id)` to delete `tasks:user:{user_id}:*` and `tasks:admin:*`.
- **Task Update (`PUT /tasks/{id}`):** Calls `invalidate_task_caches(task.user_id)` to purge modified task lists.
- **Task Deletion (`DELETE /tasks/{id}`):** Captures the owner ID before record deletion and purges associated cache patterns.

### 4. TTL Choice & Stale-Data Risk Mitigation

- **TTL Selection (`60 seconds`):** A short default expiration window (`REDIS_CACHE_TTL_SECONDS=60`) balances cache reuse during active browsing with tight consistency.
- **Stale-Data Risk:** If an unexpected database modification occurs outside standard application workflows, stale entries naturally expire within 60 seconds, acting as a safety net behind explicit invalidation.

### 5. Resilient Error Handling & Graceful Degradation

Redis is treated as an optimization layer, not a critical single point of failure:

- All Redis commands in `services/cache_service.py` are wrapped in `try / except redis.RedisError` blocks.
- If Redis is unavailable, restarts, or times out (`socket_connect_timeout=2`), the error is logged as a warning, and the service returns `None` on reads or `False` on writes.
- **Graceful Fallback:** The application transparently falls back to querying PostgreSQL directly rather than allowing Redis failure to become an API `500 Internal Server Error`. Internal Redis connection details are not exposed in error responses.

---

## API Abuse Protection & Rate Limiting (Bonus)

To prevent brute-force credential guessing and reduce CPU exhaustion from repetitive Bcrypt operations, an atomic Redis rate limiter is attached to the authentication endpoint:

- **Target Endpoint:** `POST /auth/token`
- **Threshold:** 5 requests per 60-second window per client IP address.
- **Mechanism (`dependencies/rate_limiter.py`):**
  1. Computes the key `rate_limit:login:{client_ip}`.
  2. Atomically increments the counter using Redis `INCR`.
  3. Sets a 60-second TTL on the first request via Redis `EXPIRE`.
  4. If the count exceeds 5, immediately raises `HTTP 429 Too Many Requests`.

- **Fail-Open Policy:** If Redis encounters a connection issue during rate checking, the exception is caught, logged, and the request is permitted through to avoid locking out legitimate users during infrastructure hiccups.

---

## OpenAPI Metadata & Interactive Swagger UI Documentation

The API includes comprehensive OpenAPI 3.0 specifications accessible interactively at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Key Documentation Features

1. **Global API Metadata (`main.py`)**:
   - Explicit application `title`, custom `description`, semantic `version="1.0.0"`, and `contact` maintainer information.
   - Structured `openapi_tags` definitions adding detailed section descriptions to top-level category headers in Swagger UI.

2. **Tag Hierarchy & Disambiguation**:
   - Each endpoint module declares its single authoritative tag within its `APIRouter` declaration (`tags=["Authentication"]`, `tags=["Tasks"]`, `tags=["Users"]`, `tags=["Items"]`, `tags=["External Services"]`).
   - Routers are attached in `main.py` using `app.include_router(router)` without redundant tags to prevent UI duplication.

3. **Route Annotations & Contracts**:
   - Every route decorator includes explicit `summary`, `description`, `response_description`, and mapped status code response contracts (`responses={...}`), including `429 Too Many Requests` on `/auth/token`.

4. **Rich Schema Metadata & Examples**:
   - Request and response models utilize `Field()` parameters defining titles, descriptions, validation bounds, and concrete `json_schema_extra` example payloads.

---

## Environment & Security Configuration

Database connection strings, Redis configuration, CORS origins, and cryptographic secrets are loaded dynamically at runtime using `pydantic-settings` from `.env` via `config.py`.

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
   ALLOWED_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

   # Redis Configuration
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=
   REDIS_CACHE_TTL_SECONDS=60
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

   - **Generate a new migration script:**

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
   ALLOWED_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","https://your-app-domain.com"]
   ```

---

## Prerequisites & Setup Guide

### 1. Prerequisites

- Python 3.10+
- PostgreSQL database running locally
- Redis server running locally (or via Docker)

### 2. Starting Redis via Docker

If Redis is not installed as a local system service, start an isolated container via Docker Desktop:

```cmd
docker run -d --name redis-server -p 6379:6379 redis:alpine
```

Verify the container is active:

```cmd
docker ps
```

### 3. Environment Setup

Activate your virtual environment and install dependencies:

```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

Create your local environment file by copying the template:

```cmd
copy .env.example .env
```

_Note: Update `.env` with your local PostgreSQL credentials, Redis connection settings, and secret keys._

### 4. Database Migrations

Run Alembic migrations to build required database tables (`users`, `tasks`):

```cmd
alembic upgrade head
```

Verify current migration revision status:

```cmd
alembic current
```

### 5. Application Startup

Start the FastAPI server using Uvicorn:

```cmd
uvicorn main:app --reload
```

The interactive Swagger API documentation will be available at `http://127.0.0.1:8000/docs`.

### 6. Execute Automated Tests

Run the integration test suite using isolated in-memory SQLite and clean Redis fixtures:

```cmd
pytest -v --cov
```

---

## Request Logging & Observability

The application includes production-friendly request logging middleware (`RequestLoggingMiddleware`) and a centralized logger (`logger.py`) to provide real-time visibility into API performance and endpoint usage.

### Logging Features

- **Monotonic Duration Measurement:** Uses `time.perf_counter()` to calculate total request execution duration accurately in milliseconds without risk of system clock adjustments skewing results.
- **Request Correlation IDs (`X-Request-ID`):** Reuses an incoming `X-Request-ID` HTTP header or generates a unique UUID4 per request, attaching it to both stdout log entries and outgoing response headers for end-to-end request tracing.
- **Safe Logging Practices:** Captures high-level request metadata (method, URL path, HTTP status code, duration, request ID). Sensitive data (passwords, tokens, credentials) is strictly excluded.

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

---

## Background Tasks & Reliability Architecture

### How Background Tasks Work in This Project

FastAPI's built-in `BackgroundTasks` system runs non-critical callables **after** the HTTP response has been dispatched to the client. Every successful `POST /tasks` call schedules structured audit logging via `log_task_event` in `services/audit.py`:

```python
@router.post("/tasks", status_code=201)
def create_task(payload: TaskCreate, background_tasks: BackgroundTasks, ...):
    task = task_service.create_task(...)
    background_tasks.add_task(log_task_event, task.id, task.user_id, "TASK_CREATED")
    return task
```

**Execution order:**

1. The task is written to the database and committed.
2. The `201 Created` response is returned to the client.
3. `log_task_event(...)` runs inside the same worker process; no separate queue worker or external task infrastructure is required.

The audit function is designed to catch logging failures so that a background logging failure does **not** propagate back to the HTTP response layer:

```python
def log_task_event(task_id: int, user_id: int, event_type: str) -> None:
 try:
     logger.info(f"[AUDIT] event={event_type} task_id={task_id} user_id={user_id}")
 except Exception as exc:
     logger.error(f"[AUDIT] Background task failed: {exc}")
```

### Why In-Process `BackgroundTasks` Is Used Here

This project uses `BackgroundTasks` because it satisfies the requirements with **zero external queue infrastructure**:

- No Redis, RabbitMQ, or separate worker processes are required for audit logging.
- No additional queue dependency is needed in `requirements.txt`.
- Tasks complete within the same request lifecycle, making the behavior simple to reason about and test deterministically. Starlette's `TestClient` executes background tasks synchronously before `.post()` returns.

This is appropriate for **development environments**, **low-traffic APIs**, and **non-critical side effects** such as structured audit logging.

### When a Production System Requires a Durable Queue

In-process `BackgroundTasks` have a fundamental limitation: **if the worker process crashes or is restarted while a background task is executing, that task can be lost.** There is no durable persistence or broker-managed retry mechanism.

Upgrade to a durable queue (such as **Celery + Redis** or **RQ + Redis**) when any of the following apply:

| Scenario                                       | In-Process `BackgroundTasks`  |           Celery / RQ + Redis           |
| :--------------------------------------------- | :---------------------------: | :-------------------------------------: |
| Worker crash drops the task                    |      ❌ Task can be lost      |        ✅ Task survives restart         |
| Automatic retry on failure                     |       ❌ Not supported        |     ✅ Configurable retry + backoff     |
| Sending transactional emails                   |           ❌ Risky            |          ✅ Reliable delivery           |
| Charging payment or calling billing APIs       |          ❌ Not safe          | ✅ Durable/idempotent workflow possible |
| High-volume async workload                     | ❌ Shares web-worker capacity |         ✅ Isolated worker pool         |
| Visibility into queued / failed jobs           |            ❌ None            |        ✅ Queue monitoring tools        |
| Zero queue infrastructure requirement          |     ✅ No broker required     |       ❌ Requires broker + worker       |
| Simple structured audit logging (this project) |         ✅ Sufficient         |               ⚠️ Overkill               |

### Summary

The in-process `BackgroundTasks` approach is intentional and appropriate for this project's scope. The audit log is a **non-critical side effect**: a failure to log must never fail an API response, and occasional log loss under a worker crash is acceptable. If the project is later extended with business-critical asynchronous operations such as email delivery or payment/billing workflows, `log_task_event` should be moved to a durable queue-backed worker system.

---

## Automated Testing & Verification Strategy

The repository includes a comprehensive integration test suite configured with Pytest, `TestClient`, and code coverage reporting (`pytest-cov`).

### Verification Strategy & Test Isolation

- **In-Memory SQLite Engine:** Database tests execute against an isolated SQLite database held entirely in system memory (`sqlite:///:memory:`). Production PostgreSQL data is not used during test runs.
- **FastAPI Dependency Overrides:** `tests/conftest.py` utilizes `app.dependency_overrides[get_db]` to substitute production database sessions with temporary test sessions.
- **Per-Test Schema Lifecycle:** The `db_session` fixture creates the required schema before each test and drops it immediately afterward, preventing leftover database state from contaminating later tests.
- **Redis Test Isolation:** An `autouse=True` fixture (`clean_redis`) in `tests/conftest.py` flushes Redis before and after each test function, ensuring cache isolation across tests.
- **End-to-End Registration-to-Task Workflow:** `test_complete_task_lifecycle` in `tests/test_tasks.py` exercises registration, login, task creation, retrieval, update, deletion, and cleanup verification.
- **Unauthenticated Protection & Duplicate Handling:** Integration tests verify that protected task endpoints return `401 Unauthorized` without a Bearer token and that duplicate task titles return `409 Conflict`.
- **RBAC & Default Role Coverage:** Tests verify newly registered users receive `role: "user"` and that standard users receive `403 Forbidden` for administrative actions.
- **Task Ownership & BOLA Isolation:** Tests verify `user_id` assignment, cross-user `GET`/`PUT`/`DELETE` isolation with `404 Not Found`, per-user task-list filtering, same-title support across different users, and admin access across users.
- **Network Isolation via Mocking:** `tests/test_external.py` uses `unittest.mock.patch` and `AsyncMock` to intercept external calls. Tests simulate upstream 200 OK responses, 404 Not Found errors, and 504 Timeouts locally without depending on live third-party availability.
- **Cache Miss & Hit Verification:** `test_task_list_cache_miss_then_hit` verifies that the first `GET /tasks` request populates Redis and the second request returns from cache without executing a database query.
- **Mutation Invalidation Verification:** `test_task_list_cache_invalidation_on_mutations` verifies that creating, updating, or deleting a task purges matching Redis keys after the database mutation.
- **TTL Verification:** `test_task_list_cache_ttl` verifies that cached entries receive a positive TTL conforming to the configured 60-second window.
- **Graceful Error Fallback:** `test_task_list_graceful_fallback_on_redis_error` simulates a Redis failure and confirms the endpoint can still return `200 OK` from PostgreSQL instead of failing with `500`.
- **Rate Limit Verification:** `test_login_rate_limiting` in `tests/test_auth.py` exercises `POST /auth/token` with five allowed attempts and verifies that the sixth attempt is blocked with `429 Too Many Requests`.

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
  "status": "ok"
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
  "email": "user@example.com",
  "role": "user"
}
```

### 3. Obtain Access Token with Rate Limiting (`POST /auth/token`)

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

- **Response (`429 Too Many Requests` - after 5 attempts in 60s):**

```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

### 4. Create Protected Task with Cache Invalidation (`POST /tasks`)

- **Headers:**
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`

- **Request Body (JSON):**

```json
{
  "title": "Document Caching Architecture",
  "description": "Add Redis cache-aside and invalidation details to README",
  "priority": 1
}
```

- **Response (`201 Created`):**

```json
{
  "id": 1,
  "title": "Document Caching Architecture",
  "description": "Add Redis cache-aside and invalidation details to README",
  "priority": 1,
  "status": "pending",
  "is_completed": false,
  "user_id": 1
}
```

The `user_id` is assigned automatically from the authenticated user's ID; it is not supplied by the client in the task creation body.

### 5. List Tasks with Cache-Aside (`GET /tasks`)

- **Headers:** `Authorization: Bearer <access_token>`
- **Response (`200 OK`):**

```json
[
  {
    "id": 1,
    "title": "Document Caching Architecture",
    "description": "Add Redis cache-aside and invalidation details to README",
    "priority": 1,
    "status": "pending",
    "is_completed": false,
    "user_id": 1
  }
]
```

---

## Live Technical Demo Script

Follow this sequence in Swagger UI (`http://127.0.0.1:8000/docs`) to demonstrate the end-to-end user workflow, including authenticated task ownership, RBAC, caching, and rate limiting:

1. **Verify System Health (`GET /health`)**
   - **Action:** Click "Try it out" and execute `GET /health`.
   - **Expected Output:** Status `200 OK` with `{"status": "ok"}`.
   - **Talking Point:** Proves the application server is running and accepting HTTP requests.

2. **Register a User Account (`POST /auth/register`)**
   - **Action:** Submit JSON with `email` and `password`.
   - **Expected Output:** Status `201 Created` with the new user `id`, `email`, and default `role: "user"`.
   - **Talking Point:** Demonstrates account creation with password hashing before persistence.

3. **Authenticate & Obtain Token (`POST /auth/token`)**
   - **Action:** Enter email into `username` and password into `password` using form-data.
   - **Expected Output:** Status `200 OK` returning a signed JWT `access_token`.
   - **Talking Point:** Demonstrates the OAuth2 password flow together with IP-based rate limiting.

4. **Authorize Swagger UI Session**
   - **Action:** Copy the `access_token`, click the **Authorize** lock button, paste the token, and authorize.
   - **Talking Point:** Attaches the Bearer token header to subsequent protected requests.

5. **Create Protected Task (`POST /tasks`)**
   - **Action:** Submit task JSON containing `title`, `description`, and `priority`.
   - **Expected Output:** Status `201 Created` with the created task details including `user_id`.
   - **Talking Point:** Demonstrates protected route authorization and automatic task ownership assignment.

6. **List Tasks and Demonstrate Cache-Aside (`GET /tasks`)**
   - **Action:** Execute `GET /tasks` twice with the same pagination parameters.
   - **Expected Output:** Both requests return `200 OK`.
   - **Talking Point:** The first request is a cache miss that queries PostgreSQL; the second can be served from Redis until the 60-second TTL expires.

---

## Verification Workflow via Swagger UI & Pytest

### 1. Automated Verification (CLI)

Run `pytest -v --cov` and confirm the suite covers root health, user registration, default role assignment, token login, complete task CRUD, task ownership isolation, RBAC restrictions, BOLA-safe `404 Not Found` behavior, duplicate title conflicts (`409`), pagination, unauthenticated route protection (`401`), input validation (`422`), mocked external service behavior (`200`, `404`, `504`), cache hit/miss behavior, cache invalidation, TTL enforcement, Redis graceful fallback, and rate limiting (`429`).

### 2. Manual Verification (Swagger UI)

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Interactive OpenAPI Metadata & Category Headers:**
   - Confirm title, description, contact details, and version reflect application metadata.
   - Verify category descriptions under `Health`, `Authentication`, `Tasks`, `Users`, `Items`, and `External Services`.
   - Confirm no duplicate endpoint listings or duplicate tag categories exist.

3. **Verify Protected Task Authorization & Ownership (`POST /tasks`, `GET /tasks`, `GET/PUT/DELETE /tasks/{task_id}`):**
   - Execute `GET /tasks` without authorization -> confirm `401 Unauthorized`.
   - Register a user, obtain a token via `POST /auth/token`, click **Authorize**, and submit `POST /tasks`. Confirm `201 Created` and a response containing the authenticated user's `user_id`.
   - Authenticate as another regular user and attempt to access, update, or delete the first user's task -> confirm `404 Not Found`.
   - Execute `GET /tasks` as each regular user -> confirm each user receives only their own tasks.
   - Authenticate as an admin -> confirm admins can retrieve and manage tasks across users.

4. **Verify Administrative Role Management (`PATCH /users/{user_id}/role`):**
   - As a regular user, attempt the role-update endpoint -> confirm `403 Forbidden`.
   - As an admin, update a user's role and confirm the action succeeds.

5. **Verify Cache-Aside Behavior (`GET /tasks`):**
   - Execute the same task-list request twice.
   - Confirm the first request can populate Redis and the repeated request can be served from cache.
   - After a task mutation, repeat the list request and confirm invalidation forces refreshed data.

6. **Verify Rate Limiting (`POST /auth/token`):**
   - Exceed five login attempts from the same client IP within the 60-second window.
   - Confirm the sixth request returns `429 Too Many Requests`.

---

## API Endpoints

| Method   | Endpoint                    | Tag Category      | Security               | Success          | Error Codes                | Description                                                               |
| :------- | :-------------------------- | :---------------- | :--------------------- | :--------------- | :------------------------- | :------------------------------------------------------------------------ |
| `GET`    | `/`                         | Health            | Public                 | `200 OK`         | —                          | Root welcome message payload                                              |
| `GET`    | `/health`                   | Health            | Public                 | `200 OK`         | —                          | System availability and health check                                      |
| `POST`   | `/auth/register`            | Authentication    | Public                 | `201 Created`    | `409`, `422`               | Register user account with password hashing                               |
| `POST`   | `/auth/token`               | Authentication    | Public (Rate Limited)  | `200 OK`         | `401`, `422`, `429`        | Authenticate credentials (max 5/min) and issue OAuth2 Bearer JWT token    |
| `PATCH`  | `/users/{user_id}/role`     | Users             | **Admin Bearer Token** | `200 OK`         | `401`, `403`, `404`, `422` | Change a user's role; restricted to admins                                |
| `POST`   | `/tasks`                    | Tasks             | **Bearer Token**       | `201 Created`    | `401`, `409`, `422`        | Create a task, audit event in background, and invalidate task list caches |
| `GET`    | `/tasks`                    | Tasks             | **Bearer Token**       | `200 OK`         | `401`, `422`               | Retrieve cached paginated tasks via Cache-Aside flow                      |
| `GET`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**       | `200 OK`         | `401`, `404`               | Retrieve a single task by ID subject to ownership check                   |
| `PUT`    | `/tasks/{task_id}`          | Tasks             | **Bearer Token**       | `200 OK`         | `401`, `404`, `409`, `422` | Update an owned task and invalidate user and admin task list caches       |
| `DELETE` | `/tasks/{task_id}`          | Tasks             | **Bearer Token**       | `204 No Content` | `401`, `404`               | Delete an owned task and invalidate user and admin task list caches       |
| `GET`    | `/items`                    | Items             | Public                 | `200 OK`         | —                          | Retrieve list of items                                                    |
| `GET`    | `/items/{item_id}`          | Items             | Public                 | `200 OK`         | `404`                      | Retrieve single item by ID                                                |
| `GET`    | `/external/posts/{post_id}` | External Services | Public                 | `200 OK`         | `404`, `502`, `504`, `422` | Asynchronously fetch external post with 5s timeout                        |

---

## Remaining Issues Checklist

### Unresolved Issues & Cleanup

- [ ] **Fix and standardize the Items module:** The Items module currently uses in-memory dictionaries. Refactor it to use PostgreSQL, SQLAlchemy models, Alembic migrations, JWT authentication (`get_current_user`), and the standardized error format.

- [ ] **Make all files consistent:** The Tasks domain features caching, logging, validation, custom exceptions, and integration tests. Align the Items and External modules with the same architectural standard.

### Future Enhancements & Practice

- [ ] **Give tasks a proper purpose & user isolation:** Task ownership and user isolation are implemented via the `user_id` foreign key. Add extended fields such as due dates and priority filters.

- [ ] **Attempt frontend integration:** Practice backend integration with an external client application instead of relying solely on Swagger UI.

---

## Definition of Done

- [x] Verified the full registration-to-authenticated-task workflow through the automated integration test suite.
- [x] Verified database isolation using the in-memory SQLite test database and FastAPI dependency overrides.
- [x] Verified authentication, protected task routes, pagination, duplicate title conflict handling (`409`), unauthenticated protection (`401`), RBAC, task ownership isolation, and BOLA-safe `404` responses.
- [x] Verified mocked external service integration covering success, `404 Not Found`, and `504 Timeout` scenarios.
- [x] Verified OpenAPI metadata, Swagger UI documentation, request logging, correlation IDs, and CORS configuration.
- [x] Implemented `services/audit.py` `log_task_event` with resilient `try/except` handling and wired it to `POST /tasks` via FastAPI `BackgroundTasks` after successful persistence.
- [x] Verified background task integration for successful task creation, failure isolation, and API resilience when background logging fails.
- [x] Documented `BackgroundTasks` versus durable queue (Celery/RQ) trade-offs and execution characteristics.
- [x] Implemented Redis configuration via `pydantic-settings` (`config.py`) and documented environment keys in `.env.example`.
- [x] Created `services/cache_service.py` with `get_cache`, `set_cache`, `delete_cache`, and pattern-based purging with resilient fallback.
- [x] Integrated cache-aside read behavior on `GET /tasks` with user-scoped and admin-scoped pagination keys.
- [x] Wired cache invalidation to `POST /tasks`, `PUT /tasks/{id}`, and `DELETE /tasks/{id}` after successful database commits.
- [x] Verified cache miss, cache hit (zero DB queries), 60-second TTL enforcement, and mutation invalidation through automated tests.
- [x] Added IP-based authentication rate limiting (5 attempts/minute per client IP) on `POST /auth/token` with automated test verification.
- [x] Documented TTL trade-offs, stale-data mitigation, and graceful Redis degradation in `README.md`.
- [x] Updated `README.md` to reflect the current Day 19 architecture, setup workflow, caching, rate limiting, API examples, verification workflow, and project status.

---

## Project Retrospective & Future Improvements

### 1. Significant Technical Challenges

Two major integration concerns shaped the Day 19 implementation:

- Earlier integration tests could contaminate later tests through shared database state, causing failures such as duplicate email conflicts and unexpected pagination counts.
- Introducing Redis cache-aside behavior created stale-data risks after task creation, updates, or deletion. Testing Redis also exposed client-library type-checking issues and failures when no Redis instance was available.

### 2. Resolution Strategy

- Configured `tests/conftest.py` to use an isolated in-memory SQLite database and a per-test schema lifecycle, connected to FastAPI with `app.dependency_overrides[get_db]`.
- Added a `clean_redis` autouse fixture with guarded cleanup and documented Docker-based Redis startup for reliable local testing.
- Implemented `invalidate_task_caches` immediately after successful database commits on `create_task`, `update_task`, and `delete_task`, purging user and admin cached pages via pattern matching.
- Applied `typing.cast` in test assertions where required to satisfy static type checkers without changing runtime behavior.
- Wrapped Redis operations in `services/cache_service.py` with `try / except redis.RedisError` so the API degrades to PostgreSQL when Redis is unavailable.

### 3. Key Learning Outcome

Gained practical experience with FastAPI dependency overrides and test isolation, along with a deeper understanding of the **Cache-Aside** pattern, post-commit cache invalidation, rate limiting, and designing Redis as a non-fatal optimization layer.

### 4. Actionable Future Improvement

Extend Redis caching beyond task listings to individual task reads (`GET /tasks/{task_id}`) and consider a sliding-window rate limiter using Redis sorted sets (`ZSET`) for finer-grained request smoothing across higher-traffic routes.
