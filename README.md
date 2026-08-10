# FastAPI Internship Project - Day 2

A clean, production-aligned FastAPI application establishing core REST API routes, strict Pydantic data validation schemas, $O(1)$ in-memory dictionary storage, custom HTTP status codes, and automatic OpenAPI schema documentation.

## Objective & Scope

- **Objective:** Extend core FastAPI functionality with validated resource models, request body parsing, custom response schemas, and strict data constraints.
- **Scope:** Includes core system routes (`/`, `/health`), optimized item endpoints (`/items`, `/items/{item_id}`), and task resource management (`POST /tasks`, `GET /tasks/{task_id}`) using Pydantic models (`TaskCreate`, `TaskRead`, `ItemRead`). Persistent external database storage, authentication, and frontends are excluded.

## Project Structure

```text
fastapi-internship/
├── .gitignore          # Prevents tracking venv/ and build artifacts
├── main.py             # Application entry point, Pydantic models, and route handlers
├── README.md           # Environment setup, startup steps, endpoint specs, and verification
└── requirements.txt    # Frozen dependency versions for clean reproduction
```

## Prerequisites

- Python 3.10+
- Git

## Environment Setup & Dependency Installation

1. **Clone the repository and enter the directory:**

   ```cmd
   git clone <repository-url>
   cd fastapi-internship
   ```

2. **Create and activate a Python virtual environment:**

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install project dependencies:**

   ```cmd
   pip install -r requirements.txt
   ```

## Running the Application

Start the Uvicorn ASGI server with hot-reloading enabled:

```cmd
uvicorn main:app --reload
```

- **Server Base URL:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs:** `http://127.0.0.1:8000/docs`

## Data Validation & Pydantic Schemas

- **`ItemRead`**: Validates outbound item responses (`id > 0`, `name min_length=2`, `price gt=0`).
- **`TaskCreate`**: Validates inbound task creation requests (`title min_length=1`, `description`, `priority` constrained between `1` and `5`, `status` restricted to `"pending" | "in_progress" | "completed"`).
- **`TaskRead`**: Extends `TaskCreate` by appending the server-generated `id: int` field for outbound responses.

## API Endpoints

| Method | Endpoint | Request Schema | Response Schema | Status Code | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | None | `200 OK` | Root welcome message |
| `GET` | `/health` | None | None | `200 OK` | Operational status check |
| `GET` | `/items` | None | `list[ItemRead]` | `200 OK` | Retrieve all items |
| `GET` | `/items/{item_id}` | Path Parameter | `ItemRead` | `200 OK` / `404` | Retrieve item by ID ($O(1)$ lookup) |
| `POST` | `/tasks` | `TaskCreate` | `TaskRead` | `201 Created` / `422` | Parse, validate, and store a new task |
| `GET` | `/tasks/{task_id}` | Path Parameter | `TaskRead` | `200 OK` / `404` | Retrieve task by ID ($O(1)$ lookup) |

## Verification & Interactive Docs

1. Open `http://127.0.0.1:8000/docs` in your browser.
2. **Valid Task Creation Flow (`POST /tasks`):**
   ```json
   {
     "title": "Set up CI/CD pipeline",
     "description": "Configure GitHub Actions",
     "priority": 2,
     "status": "pending"
   }
   ```
   *Expected Outcome:* `201 Created` with auto-generated `"id": 2`.
3. **Invalid Flow - Blank Title (`POST /tasks`):**
   ```json
   {
     "title": "",
     "description": "Testing empty string",
     "priority": 1
   }
   ```
   *Expected Outcome:* `422 Unprocessable Entity` (`String should have at least 1 character`).
4. **Invalid Flow - Out of Range Priority (`POST /tasks`):**
   ```json
   {
     "title": "Invalid Priority",
     "description": "Out of range test",
     "priority": 10
   }
   ```
   *Expected Outcome:* `422 Unprocessable Entity` (`Input should be less than or equal to 5`).

## Definition of Done Verification

- [x] Application executes cleanly with `uvicorn main:app --reload`.
- [x] `TaskCreate` enforces field constraints (`min_length=1` for title, `1 <= priority <= 5`, and restricted status enum).
- [x] `TaskRead` and `ItemRead` models guarantee consistent response schemas in Swagger `/docs`.
- [x] `POST /tasks` assigns incremental IDs and returns `201 Created`.
- [x] `GET /tasks/{task_id}` and `GET /items/{item_id}` perform $O(1)$ key lookups and return `404 Not Found` for missing resources.
- [x] Malformed requests trigger structured HTTP `422 Unprocessable Entity` validation errors.
- [x] No secrets or environment configuration artifacts committed.
