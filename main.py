from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.api.llm_chat_route import router as chat_router
from app.api.chat_history_route import router as history_router


# FastAPI App Initialization
app = FastAPI(
    title="PetPal",
    description="Virtual Pet Simulator.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(history_router, prefix="/api/v1", tags=["Chat History"]) 
docs_dir = os.path.join(os.path.dirname(__file__), "docs", "spec")
if os.path.isdir(docs_dir):
    app.mount("/spec", StaticFiles(directory=docs_dir), name="spec")


def _read_doc_html(name: str) -> str:
    docs_root = os.path.join(os.path.dirname(__file__), "docs")
    file_path = os.path.join(docs_root, name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<html><body><h1>Documentation page not found</h1></body></html>"


@app.get('/swagger', include_in_schema=False)
def swagger_ui():
    html = _read_doc_html("swagger.html")
    return HTMLResponse(html)


@app.get('/redoc', include_in_schema=False)
def redoc_ui():
    html = _read_doc_html("redoc.html")
    return HTMLResponse(html)

# Health Endpoints
@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8084))
    uvicorn.run(app, host="0.0.0.0", port=port)

