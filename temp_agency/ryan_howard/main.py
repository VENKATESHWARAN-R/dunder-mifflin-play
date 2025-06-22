# main.py
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Import your A2A app instance
from ryan_howard.a2a_server import app as a2a_app
from ryan_howard.a2a_server import lifespan as a2a_lifespan

# === Configuration for UI app ===
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DB_URL = os.environ.get("DATABASE_URL", "sqlite:///./session.db")
TRACE_TO_CLOUD = os.environ.get("TRACE_TO_CLOUD", "true").lower() in (
    "true",
    "1",
    "yes",
)
ARTIFACT_SERVICE_URI = os.environ.get("ARTIFACT_SERVICE_URI", None)
MEMORY_SERVICE_URI = os.environ.get("MEMORY_SERVICE_URI", None)
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SERVE_WEB_INTERFACE = True

# Mount the Google-ADK UI app at root (or under /ui)
ui_app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    trace_to_cloud=TRACE_TO_CLOUD,
)


@asynccontextmanager
async def combined_lifespan(host_app: FastAPI):
    # Enter the A2A lifespan context
    async with a2a_lifespan(a2a_app):
        # (UI has no special startup/shutdown to run)
        yield


# Create the “host” FastAPI app
app = FastAPI(
    title="Combined Server",
    description="UI + A2A endpoints in one process",
    lifespan=combined_lifespan,
)

#
# Mount the A2A JSON-RPC server under /a2a
app.mount("/a2a", a2a_app, name="a2a")


# Optional: keep a unified health check
@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Combined server is running"}


app.mount("/", ui_app, name="ui")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
