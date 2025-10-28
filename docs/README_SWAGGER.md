# PetPal — Swagger / OpenAPI Documentation

This document explains how to view and use the API documentation for the PetPal project.

Files added
- `docs/openapi.yaml` — Hand-crafted OpenAPI 3.0.3 specification derived from the codebase.

Quick notes
- The project is a FastAPI application. When the server is running the interactive docs are automatically available at:
  - Swagger UI: `http://localhost:8084/docs`
  - ReDoc: `http://localhost:8084/redoc`
  - Raw OpenAPI JSON: `http://localhost:8084/openapi.json`

How to run (development)
1. Ensure your environment variables are set (see `.env` / `decouple` usage in code):
   - `MONGO_URI` (required)
   - `GROQ_API_KEY` (for the LLM client)

2. Start the app (examples below use PowerShell):

```powershell
python main.py
# or using uvicorn directly (recommended for dev):
uvicorn main:app --host 0.0.0.0 --port 8084
```

Viewing Swagger
- Open a browser and go to `http://localhost:8084/docs` to use Swagger UI and exercise endpoints interactively.

Static / Offline Swagger UI
- The project now includes a small helper and mounting so you can serve a static
  Swagger UI that loads the local `docs/openapi.yaml` at `http://localhost:8084/swagger`.

1. Optionally synchronize the `docs/openapi.yaml` with the live app by running:

```powershell
python scripts\export_openapi.py
```

This imports the `app` from `main.py` and writes `docs/openapi.json` and
`docs/openapi.yaml` from the app's current `app.openapi()` output.

2. Start the app and open:

  - `http://localhost:8084/swagger` — a simple Swagger UI that points at `/spec/openapi.yaml`.

Notes:
- The `/swagger` HTML currently loads Swagger UI assets from a CDN for simplicity.
  If you need fully offline docs, download the `swagger-ui` distribution into
  `docs/swagger-ui/` and modify the HTML in `main.py` to reference the local files.

Auth
- The `POST /api/v1/chat` endpoint requires an `Authorization` header. The route code only validates presence of the header, so include a token string in the header. Example header:

  Authorization: Bearer <token>

Examples
- Chat (form fields):

```powershell
curl -X POST "http://localhost:8084/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Accept: application/json" \
  -F "user_id=123" \
  -F "pet_id=456" \
  -F "message=Hello pupper!"
```

- History (JSON body):

```powershell
curl -X POST "http://localhost:8084/api/v1/history" \
  -H "Content-Type: application/json" \
  -d '{"user_id":123,"pet_id":456}'
```

Notes & Caveats
- The OpenAPI file documents the observed behavior and types inferred from the code. If you change parameter types or route signatures, please update `docs/openapi.yaml`.
- Error responses are documented generically. Specific error payloads may vary (FastAPI uses `{"detail": ...}` by default).

Next steps (recommended)
- Keep `docs/openapi.yaml` in sync with code; one approach is to export the running FastAPI `/openapi.json` and use it as a canonical source.
- Optionally mount the YAML/JSON into a static Swagger UI for offline browsing.
- Add authentication semantics (scopes, tokens) to `components.securitySchemes` if you implement strict token validation.
