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

# Serve local docs/spec folder so the OpenAPI YAML/JSON can be loaded by a static Swagger UI
# The export script writes into `docs/spec/` so mount that exact folder at /spec
docs_dir = os.path.join(os.path.dirname(__file__), "docs", "spec")
if os.path.isdir(docs_dir):
    # mount at /spec so the file is available at /spec/openapi.yaml
    app.mount("/spec", StaticFiles(directory=docs_dir), name="spec")


SWAGGER_HTML = """
<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>PetPal Swagger UI</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/spec/openapi.yaml',
                    dom_id: '#swagger-ui',
                    presets: [SwaggerUIBundle.presets.apis],
                    layout: 'BaseLayout',
                });
                window.ui = ui;
            };
        </script>
    </body>
</html>
"""


@app.get('/swagger', include_in_schema=False)
def swagger_ui():
        """Simple Swagger UI page that loads the local `docs/openapi.yaml` spec.

        Note: This HTML loads Swagger UI assets from a CDN. If you need fully offline
        Swagger UI, download the `swagger-ui` dist files into `docs/swagger-ui/` and
        update the HTML to load them locally.
        """
        return HTMLResponse(SWAGGER_HTML)

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

