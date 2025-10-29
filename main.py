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
        return HTMLResponse(SWAGGER_HTML)


REDOC_HTML = """
    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8" />
            <title>PetPal API Reference (ReDoc)</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
                .header { display:flex; align-items:center; gap:16px; padding:16px; background:#0f1724; color:#fff; }
                .header .title { font-size:20px; font-weight:600; }
                .header .subtitle { font-size:13px; opacity:0.85 }
                .tools { margin-left:auto; display:flex; gap:8px; }
                .container { display:flex; gap:24px; }
                .panel { width:320px; padding:18px; background:#f7fafc; border-right:1px solid #e2e8f0; height:calc(100vh - 64px); overflow:auto }
                .panel h3 { margin-top:0 }
                .panel pre { background:#0b1220; color:#e6eef8; padding:10px; border-radius:6px; overflow:auto }
                #redoc-container { flex:1; height: calc(100vh - 64px); }
                a.button { background:#2563eb; color:#fff; padding:8px 10px; border-radius:6px; text-decoration:none; font-size:13px }
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <div class="title">PetPal — API Reference</div>
                    <div class="subtitle">Virtual Pet Simulator — interactive API docs (ReDoc)</div>
                </div>
                <div class="tools">
                    <a class="button" href="/docs" target="_blank">Swagger UI</a>
                    <a class="button" href="/spec/openapi.yaml" target="_blank">OpenAPI YAML</a>
                </div>
            </div>
            <div class="container">
                <div class="panel" aria-hidden="false">
                    <h3>Quickstart</h3>
                    <p>Use the interactive ReDoc viewer to explore endpoints, schemas and examples. The static spec is served from <code>/spec/openapi.yaml</code>.</p>

                    <h3>Authentication</h3>
                    <p>The <code>/api/v1/chat</code> endpoint requires an <code>Authorization</code> header (Bearer token). The server currently checks for presence only.</p>
                    <pre>Authorization: Bearer &lt;token&gt;</pre>

                    <h3>Example: Chat</h3>
                    <pre>curl -X POST "http://localhost:8084/api/v1/chat" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        -H "Accept: application/json" \
        -F "user_id=123" \
        -F "pet_id=456" \
        -F "message=Hello pupper!"</pre>

                    <h3>Example: History</h3>
                    <pre>curl -X POST "http://localhost:8084/api/v1/history?user_id=123&pet_id=456"</pre>

                    <h3>Notes</h3>
                    <ul>
                        <li>To regenerate the spec from the running app: <code>python scripts/export_openapi.py</code></li>
                        <li>If ReDoc fails to load, confirm <code>/spec/openapi.yaml</code> is reachable and that the server was restarted after changes.</li>
                    </ul>
                </div>
                <div id="redoc-container">
                    <!-- ReDoc will render here -->
                </div>
            </div>

            <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
            <script>
                // Render ReDoc with the local spec
                Redoc.init('/spec/openapi.yaml', {
                    scrollYOffset: '64',
                    hideHostname: true,
                    theme: { colors: { primary: { main: '#2563eb' } } }
                }, document.getElementById('redoc-container'));
            </script>
        </body>
    </html>
    """


@app.get('/redoc', include_in_schema=False)
def redoc_ui():
            """Custom ReDoc page that loads the static OpenAPI spec and provides
            quickstart instructions, examples, and links to the YAML/Swagger UI.
            """
            return HTMLResponse(REDOC_HTML)

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

