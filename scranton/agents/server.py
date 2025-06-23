import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

BASE_DIR = os.path.dirname(__file__)
SESSION_DB_URL = os.environ.get("DATABASE_URL", "sqlite:///./session.db")
TRACE_TO_CLOUD = os.environ.get("TRACE_TO_CLOUD", "false").lower() in ("true","1","yes")
ARTIFACT_SERVICE_URI = os.environ.get("ARTIFACT_SERVICE_URI")
MEMORY_SERVICE_URI = os.environ.get("MEMORY_SERVICE_URI")
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SERVE_WEB_INTERFACE = True

print(f"BASE_DIR: {BASE_DIR}")
print(f"SESSION_DB_URL: {SESSION_DB_URL}")
print(f"TRACE_TO_CLOUD: {TRACE_TO_CLOUD}")

app = get_fast_api_app(
    agents_dir=BASE_DIR,
    session_service_uri=SESSION_DB_URL,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    trace_to_cloud=TRACE_TO_CLOUD,
)

@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
