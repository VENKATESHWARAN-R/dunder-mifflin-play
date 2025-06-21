import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = os.environ.get("DATABASE_URL", "sqlite:///./session.db")
# Enable Tracing to Google Cloud
TRACE_TO_CLOUD = os.environ.get("TRACE_TO_CLOUD", "true").lower() in ("true", "1", "yes")
# Artifact service URI (if applicable)
ARTIFACT_SERVICE_URI = os.environ.get("ARTIFACT_SERVICE_URI", None)
# Memory service URI (if applicable)
MEMORY_SERVICE_URI = os.environ.get("MEMORY_SERVICE_URI", None)
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# printing configuration for debugging purposes
print(f"AGENT_DIR: {AGENT_DIR}")
print(f"ARTIFACT_SERVICE_URI: {ARTIFACT_SERVICE_URI}")
print(f"MEMORY_SERVICE_URI: {MEMORY_SERVICE_URI}")
print(f"ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
print(f"SERVE_WEB_INTERFACE: {SERVE_WEB_INTERFACE}")
print(f"TRACE_TO_CLOUD: {TRACE_TO_CLOUD}")

print("Starting FastAPI server...")
# Call the function to get the FastAPI app instance
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    artifact_service_uri=ARTIFACT_SERVICE_URI,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    trace_to_cloud=TRACE_TO_CLOUD
)


@app.get("/healthz")
def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok", "message": "Server is running"}


if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
