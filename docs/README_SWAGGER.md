# PetPal — Swagger / OpenAPI Documentation

This document explains how to view, update, and use the **API documentation** for the PetPal project.

---

## 🚀 Quick Notes

The project is a **FastAPI** application.  
When the server is running, you can access documentation through:

| Type | URL | Description |
|------|-----|--------------|
| Swagger UI (interactive) | [http://localhost:8084/docs](http://localhost:8084/docs) | FastAPI’s default interactive documentation |
| ReDoc (static viewer) | [http://localhost:8084/redoc](http://localhost:8084/redoc) | Clean read-only OpenAPI view |
| Static Swagger UI | [http://localhost:8084/swagger](http://localhost:8084/swagger) | Custom Swagger UI loading your static YAML |
| Raw YAML Spec | [http://localhost:8084/spec/openapi.yaml](http://localhost:8084/spec/openapi.yaml) | Raw OpenAPI YAML served statically |
| Raw JSON Spec | [http://localhost:8084/spec/openapi.json](http://localhost:8084/spec/openapi.json) | Raw OpenAPI JSON served statically |

---

## How to Run (Development)

1. **Set your environment variables** (`.env` or system environment):

   - `MONGO_URI` — MongoDB connection string  
   - `GROQ_API_KEY` — API key for the LLM client  

2. **Start the app** (examples below use PowerShell):

```powershell
# Run via main.py
python main.py

# or directly with Uvicorn (recommended for development)
uvicorn main:app --host 0.0.0.0 --port 8084
```

## 📘 Viewing API Documentation

1. FastAPI built-in docs

   - Swagger UI: http://localhost:8084/docs

   - ReDoc: http://localhost:8084/redoc

2. Static / Offline Swagger UI

   PetPal includes a static Swagger UI page that loads the hand-written spec:

   Open: http://localhost:8084/swagger

   This loads /spec/openapi.yaml, which lives in docs/spec/.

   If you ever want to regenerate the spec automatically from your live FastAPI app:

```powershell
python scripts\export_openapi.py
```

   That command will write:

   - `docs/spec/openapi.json`
   - `docs/spec/openapi.yaml`

## Authentication

The API currently requires a simple Bearer token for the `/api/v1/chat` endpoint.
It is validated only for presence, not for content (for now).

Example header:

```makefile
Authorization: Bearer <token>
```

Swagger UI includes an Authorize 🔒 button to input your token interactively.

## 💬 Example Requests

> Chat (form fields)

Sends a message to the AI pet and receives a short, expressive reply.

```powershell
curl -X POST "http://localhost:8084/api/v1/chat" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -H "Accept: application/json" ^
  -F "user_id=123" ^
  -F "pet_id=456" ^
  -F "message=Hello pupper!"
```

Response example:

```json
{
  "response": "(happy) {wag tail} <bark> Missed you! Play time?",
  "features": {
    "motions": ["wag tail"],
    "sounds": ["bark"],
    "emotions": ["happy"]
  }
}
```

> History (query parameters)

Retrieves past chat messages between a user and a pet.

```powershell
curl -X POST "http://localhost:8084/api/v1/history?user_id=123&pet_id=456"
```

Response (truncated):

```json
[
  { "sender": "user", "text": "Hi!", "timestamp": "2025-10-28T02:00:00Z" },
  { "sender": "ai", "text": "(happy) {wag tail} <bark> Hello!", "timestamp": "2025-10-28T02:00:01Z" }
]
```

