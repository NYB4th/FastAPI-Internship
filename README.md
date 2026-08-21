# FastAPI Internship Project - Day 9

A modular, enterprise-structured FastAPI application featuring secure user registration, JWT-based authentication, OAuth2 password flow, dependency-driven route authorization, database-backed CRUD operations, database-level query pagination, and schema version control using Alembic database migrations. The system manages PostgreSQL persistent state via SQLAlchemy ORM, enforcing strict domain rules, collision checks, input validation bounds, password security via Bcrypt hashing, and cryptographic token verification via PyJWT.

## Architecture Overview

This project uses a layered architecture to keep HTTP routing, business logic, security utilities, data persistence, and database migrations cleanly separated:

- **Routers (`routers/`)**: Handles incoming HTTP requests, route binding, query parameter validation (`limit`/`offset`), form data parsing (`OAuth2PasswordRequestForm`), payload parsing, and HTTP status codes (`201 Created`, `200 OK`, `204 No Content`, `401 Unauthorized`).
- **Dependencies (`dependencies/`)**: Implements reusable request authorization dependencies (`get_current_user`) using `OAuth2PasswordBearer` to extract, decode, and validate incoming Bearer tokens across protected routes.
- **Services (`services/`)**: Implements core business logic, user uniqueness checks, credential authentication (`authenticate_user`), password hashing orchestration, case-insensitive task duplicate checks, in-place ORM updates, deletion transactions, and database-level pagination queries.
- **Utils (`utils/`)**: Enforces security logic such as password hashing and verification using `pwdlib` (with explicit `BcryptHasher`), alongside JWT generation (`create_access_token`) using `PyJWT`.
- **Database (`database.py`)**: Configures the SQLAlchemy database engine, `SessionLocal` factory, declarative base, and the `get_db` generator dependency.
- **Models (`models/`)**: Defines SQLAlchemy ORM models (`User`, `Task`) representing database tables and column constraints in PostgreSQL.
- **Migrations (`alembic/`)**: Manages version-controlled database schema changes (DDL) using Alembic, dynamically bound to `Base.metadata` and environment configuration.
- **Exceptions (`exceptions/`)**: Contains custom domain exceptions (`UserAlreadyExistsError`, `TaskNotFoundError`, `TaskAlreadyExistsError`) for framework-agnostic error handling.
- **Schemas (`schemas/`)**: Defines strict Pydantic models for API request validation (`UserCreate`, `TaskCreate`, `TaskUpdate`), response serialization (`UserResponse`, `from_attributes=True`), OAuth2 tokens (`Token`, `TokenData`), and error payload contracts (`ErrorResponse`).
- **Global Handlers (`main.py`)**: Registers app startup, routers (`auth`, `task_router`, `item_router`), and global exception handlers for standardized JSON error responses.

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
│   ├── auth_exceptions.py # Auth domain exceptions (UserAlreadyExistsError)
│   └── task_exceptions.py # Task domain exceptions
├── main.py              # App initialization, routers & global error handlers
├── models/
│   ├── __init__.py
│   ├── task.py          # SQLAlchemy ORM task model
│   └── user.py          # SQLAlchemy ORM user model (users table)
├── README.md            # Architecture, database setup, and API specifications
├── requirements.txt     # Application dependencies (FastAPI, PyJWT, python-multipart, etc.)
├── routers/
│   ├── __init__.py
│   ├── auth.py          # HTTP endpoints for /auth (Registration & Token Login)
│   ├── item_router.py   # HTTP endpoints for /items
│   └── task_router.py   # HTTP endpoints for /tasks (CRUD, pagination & Auth Protection)
├── schemas/
│   ├── __init__.py
│   ├── error.py         # Standardized ErrorResponse schema
│   ├── item.py          # Item validation models
│   ├── task.py          # Task Pydantic schemas (Create, Update, Read)
│   ├── token.py         # Token & TokenData Pydantic schemas
│   └── user.py          # User Pydantic schemas (UserCreate, UserResponse)
├── services/
│   ├── __init__.py
│   ├── item_service.py  # Business logic & in-memory item store
│   ├── task_service.py  # Database CRUD operations, pagination & collision checks
│   └── user_service.py  # User creation, authentication & email uniqueness logic
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

- **Invalid Credentials Response (`401 Unauthorized`):**

```json
{
  "detail": "Incorrect email or password"
}
```

### 3. Create Task - Protected Endpoint (`POST /tasks`)

- **Header Required:** `Authorization: Bearer <access_token>`
- **Request Body:**

```json
{
  "title": "Complete Day 9 Assignment",
  "description": "Implement JWT authentication and route protection"
}
```

- **Response (`201 Created`):**

```json
{
  "title": "Complete Day 9 Assignment",
  "description": "Implement JWT authentication and route protection",
  "priority": 1,
  "status": "pending",
  "is_completed": false,
  "id": 1
}
```

- **Missing or Invalid Token Response (`401 Unauthorized`):**

```json
{
  "detail": "Could not validate credentials"
}
```

---

## API Endpoints

| Method   | Endpoint           | Security           | Layer Handling    | Success          | Error Codes         | Description                                      |
| :------- | :----------------- | :----------------- | :---------------- | :--------------- | :------------------ | :----------------------------------------------- |
| `GET`    | `/`                | Public             | `main.py`         | `200 OK`         | —                   | Root welcome payload                             |
| `GET`    | `/health`          | Public             | `main.py`         | `200 OK`         | —                   | System health check                              |
| `POST`   | `/auth/register`   | Public             | `routers/auth.py` | `201 Created`    | `409`, `422`        | Register user with Bcrypt hashing & unique check |
| `POST`   | `/auth/token`      | Public (Form Data) | `routers/auth.py` | `200 OK`         | `401`, `422`        | Verify credentials & return signed JWT token     |
| `GET`    | `/items`           | Public             | `item_router.py`  | `200 OK`         | —                   | List all items                                   |
| `GET`    | `/items/{item_id}` | Public             | `item_router.py`  | `200 OK`         | `404`               | Retrieve item by ID                              |
| `POST`   | `/tasks`           | **Bearer Token**   | `task_router.py`  | `201 Created`    | `401`, `409`, `422` | Protected: Create task for authenticated user    |
| `GET`    | `/tasks`           | Public             | `task_router.py`  | `200 OK`         | `422`               | List tasks with `limit` & `offset`               |
| `GET`    | `/tasks/{task_id}` | Public             | `task_router.py`  | `200 OK`         | `404`               | Retrieve task by ID                              |
| `PUT`    | `/tasks/{task_id}` | Public             | `task_router.py`  | `200 OK`         | `404`, `409`, `422` | Update existing task (partial/full)              |
| `DELETE` | `/tasks/{task_id}` | Public             | `task_router.py`  | `204 No Content` | `404`               | Delete task from database                        |

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

6. **Access Interactive Docs:**
   Navigate to `http://127.0.0.1:8000/docs`

---

## Verification Workflow via Swagger UI

1. Open `http://127.0.0.1:8000/docs`.
2. **Verify Denied Access (Unauthenticated):**
   - Expand `POST /tasks`, click **Try it out**, enter task details, and click **Execute**.
   - Confirm response status is `401 Unauthorized`.
3. **Register & Obtain Token (`POST /auth/token`):**
   - Register a user via `POST /auth/register` if necessary.
   - Click the green **Authorize** button at the top right of the page.
   - Enter your email in **username** and your password in **password**.
   - Click **Authorize**, then **Close**.
4. **Verify Allowed Access (Authenticated):**
   - Execute `POST /tasks` again.
   - Confirm status code is `201 Created` and the task object is returned.
5. **Verify Token Invalidation on Logout:**
   - Click **Authorize** -> **Logout**.
   - Re-execute `POST /tasks` -> Confirm response returns `401 Unauthorized`.

---

## Definition of Done

- [x] Installed and configured `PyJWT` for cryptographic token generation/validation and `python-multipart` for form decoding.
- [x] Defined `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` environment variables.
- [x] Implemented `create_access_token` utility in `utils/security.py` embedding subject (`sub`) and expiration (`exp`) claims.
- [x] Created `Token` and `TokenData` Pydantic models for OAuth2 token responses and claim validation.
- [x] Implemented `authenticate_user` service logic verifying plain passwords against stored Bcrypt hashes.
- [x] Built `/auth/token` login endpoint accepting `OAuth2PasswordRequestForm` and returning signed access tokens.
- [x] Built `get_current_user` dependency in `dependencies/auth.py` using `OAuth2PasswordBearer` to extract, decode, and validate tokens.
- [x] Protected `POST /tasks` endpoint using `current_user: User = Depends(get_current_user)`.
- [x] Verified `201 Created` responses for valid tokens and generic `401 Unauthorized` responses for missing/invalid credentials.
- [x] Documented setup, security configurations, endpoints, and verification steps in `README.md`.
