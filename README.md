# FastAPI Internship Project - Day 1

A clean, minimal FastAPI application establishing the foundational project structure, virtual environment configuration, ASGI server setup via Uvicorn, and automatic OpenAPI documentation.

## Objective & Scope

- **Objective:** Establish local development environment and implement core introductory HTTP endpoints using FastAPI.
- **Scope:** Limited to project setup, dependency capture, basic routing (`/health`, `/`, and in-memory resource `/items`), concise startup instructions, and verification evidence via `/docs`. Persistent storage, authentication, and frontends are excluded.

## Project Structure

```text
fastapi-internship/
├── .gitignore          # Prevents tracking venv/ and build artifacts
├── main.py             # Application entry point and route handlers
├── README.md           # Environment setup, startup steps, and endpoint specs
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

## API Endpoints

| Method | Endpoint           | Description                           | Expected Response                                       |
| :----- | :----------------- | :------------------------------------ | :------------------------------------------------------ |
| `GET`  | `/`                | Root welcome endpoint                 | `{"message": "Welcome to the FastAPI Internship API!"}` |
| `GET`  | `/health`          | System operational health check       | `{"status": "ok"}`                                      |
| `GET`  | `/items`           | Retrieve full list of in-memory items | `{"items": [...]}`                                      |
| `GET`  | `/items/{item_id}` | Retrieve single item by integer ID    | `{"id": 1, "name": "Wireless Mouse", "price": 25.50}`   |

## Verification & Interactive Docs

1. Navigate to `http://127.0.0.1:8000/docs` in your browser.
2. Expand each endpoint (`GET /`, `GET /health`, `GET /items`, `GET /items/{item_id}`).
3. Click **Try it out** and execute requests to verify HTTP 200 responses and correct JSON payloads.
4. Capture request/response evidence and `/docs` screenshots for submission.

## Definition of Done Verification

- [x] Application starts successfully using `uvicorn main:app --reload`.
- [x] `GET /health` returns HTTP 200 and `{"status": "ok"}` payload.
- [x] `GET /` returns HTTP 200 and welcome response.
- [x] `GET /items` and `GET /items/{item_id}` return valid JSON responses.
- [x] All endpoints are visible and testable via `/docs`.
- [x] Dependencies locked in `requirements.txt` for clean installation in fresh setups.
