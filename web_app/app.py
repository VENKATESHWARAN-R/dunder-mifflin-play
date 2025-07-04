# app.py
import os
import uuid
import psycopg2
import time
import requests
import logging
import json
from functools import wraps
from psycopg2.extras import RealDictCursor
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = os.getenv("APP_URL")
AGENT_INFO_JSON = os.getenv("AGENT_INFO_JSON", "{}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Parse agent info JSON
try:
    AGENT_INFO = json.loads(AGENT_INFO_JSON)
    logger.info(f"Loaded agent info for {len(AGENT_INFO)} agents")
except json.JSONDecodeError:
    logger.warning("Failed to parse AGENT_INFO_JSON, using empty dict")
    AGENT_INFO = {}

# Check if required environment variables are set
if not API_URL:
    logger.warning("APP_URL environment variable not set. API calls will fail.")
else:
    API_URL = API_URL.rstrip("/")  # Ensure no trailing slash


# --- Database Connection ---
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        logger.info("Connecting to database...")
        # Avoid logging the full database URL as it may contain credentials
        logger.debug("Using DATABASE_URL (redacted sensitive info)")
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Could not connect to database: {e}")
        return None


# --- Decorators ---
def login_required(f):
    """Decorator to ensure a user is logged in before accessing a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# --- Helper function to provide agent data ---
def _get_agent_list():
    """Helper function that returns the raw Python list of agent names."""
    return [
        "conference_room",
    ]


# --- Main Application Routes ---

# --- User Management & Authentication Routes ---


@app.route("/")
def root():
    """Redirects to home if logged in, otherwise to login page."""
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login and registration."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please try again later.", "danger")
            return render_template("login.html")

        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if user exists
        cur.execute("SELECT * FROM app_users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:
            # User exists, check password
            if check_password_hash(user["hashed_password"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                cur.close()
                conn.close()
                return redirect(url_for("home"))
            else:
                flash("Invalid username or password. Please try again.", "danger")
        else:
            # User does not exist, create a new one
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO app_users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                (username, hashed_password),
            )
            new_user_id = cur.fetchone()["id"]
            conn.commit()

            session["user_id"] = new_user_id
            session["username"] = username
            flash(f"Welcome, {username}! Your account has been created.", "success")

        cur.close()
        conn.close()
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# --- Main Application Routes ---


@app.route("/home")
@login_required
def home():
    """Displays the home page with a list of agents."""
    return render_template(
        "home.html", 
        username=session.get("username"),
        agent_info_json=json.dumps(AGENT_INFO)
    )


@app.route("/chat/<agent_name>")
@login_required
def chat_page(agent_name):
    """Renders the dedicated chat page for a specific agent."""
    try:
        # Get the list of valid agents from the API
        response = requests.get(f"{API_URL}/list-apps", timeout=10)
        logger.info(f"API URL: {API_URL}/list-apps | Response Status: {response.status_code}")
        logger.debug(f"Response Content: {response.text}")
        if response.status_code == 200:
            valid_agents = response.json()
            if agent_name not in valid_agents:
                flash("Invalid agent selected.", "danger")
                return redirect(url_for("home"))
        else:
            # Fall back to the helper function if API call fails
            valid_agents = _get_agent_list()
            if agent_name not in valid_agents:
                flash("Invalid agent selected.", "danger")
                return redirect(url_for("home"))
    except requests.RequestException:
        # Fall back to the helper function if API call fails
        valid_agents = _get_agent_list()
        if agent_name not in valid_agents:
            flash("Invalid agent selected.", "danger")
            return redirect(url_for("home"))

    return render_template(
        "chat.html", agent_name=agent_name, username=session.get("username")
    )


# --- API Endpoints for Chat Agents ---


@app.route("/list-apps", methods=["GET"])
@login_required
def get_list_apps():
    """Get list of available chat agents from the backend API."""
    try:
        response = requests.get(f"{API_URL}/list-apps", timeout=10)
        logger.info(f"API URL: {API_URL}/list-apps | Response Status: {response.status_code}")
        logger.debug(f"Response Content: {response.text}")
        response.raise_for_status()  # Raise exception for non-200 status codes
        return jsonify(response.json())
    except requests.RequestException as e:
        logger.error(f"Error fetching apps: {e}")
        # Fall back to local list if API call fails
        agents = _get_agent_list()
        return jsonify(agents)


@app.route("/run", methods=["POST"])
@login_required
def run_chat():
    """
    Process a chat message by forwarding to the backend API
    and return the response. Checks if session exists first and creates it if needed.
    """
    data = request.json
    app_name = data.get("app_name")
    user_id = str(session.get("user_id"))  # Use session user_id
    session_id = data.get("session_id")
    new_message = data.get("new_message")
    streaming = data.get("streaming", False)

    if not all([app_name, user_id, session_id, new_message]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # First, check if the session exists
        session_check_url = f"{API_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        
        try:
            check_response = requests.get(session_check_url, timeout=10)
            # If we get a 404 or other error, session doesn't exist
            session_exists = check_response.status_code == 200
            logger.info(f"Session check result: exists={session_exists}, status={check_response.status_code}")
        except requests.RequestException as check_err:
            session_exists = False
            logger.error(f"Error checking session existence: {check_err}")
            
        # If session doesn't exist, create it
        if not session_exists:
            logger.info(f"Session {session_id} doesn't exist. Creating it.")
            try:
                # Create a new session with default state
                create_session_payload = {
                    "state": {
                        "preferred_language": "English",
                        "visit_count": 1
                    }
                }
                create_response = requests.post(
                    session_check_url,
                    json=create_session_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                # Log session creation result
                if create_response.status_code == 200 or "already exists" in create_response.text:
                    logger.info(f"Session {session_id} created or already existed.")
                    logger.debug(f"Created session response status: {create_response.status_code}")
                else:
                    logger.warning(f"Failed to create session {session_id}: {create_response.status_code}")
                    logger.debug(f"Failed to create session response: {create_response.text}")
                    
            except requests.RequestException as session_err:
                logger.error(f"Error creating session: {session_err}")

        # Create the request payload
        payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": new_message,
            "streaming": streaming,
        }

        logger.info(f"Forwarding request to {API_URL}/run")
        logger.debug(f"Request payload: {payload}")

        # Forward the request to the backend
        response = requests.post(
            f"{API_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        logger.info(f"Response Status: {response.status_code}")
        logger.debug(f"Response Content length: {len(response.text)} characters")
        response.raise_for_status()

        # Get response data
        api_response = response.json()

        # Process the response to extract only text parts if needed
        processed_response = []
        for event in api_response:
            if "content" in event and "parts" in event["content"]:
                # Filter to only include text parts
                text_parts = []
                for part in event["content"]["parts"]:
                    if "text" in part:
                        text_parts.append({"text": part["text"]})

                if text_parts:
                    processed_event = {
                        "content": {
                            "parts": text_parts,
                            "role": event["content"].get("role", "model"),
                        },
                        "author": event.get("author", app_name),
                        "id": event.get("id", str(uuid.uuid4())),
                        "timestamp": event.get("timestamp", time.time()),
                    }
                    processed_response.append(processed_event)
        if not processed_response:
            # Add a default response if no text parts found
            fallback_text = (
                f"No text response from {app_name.replace('_', ' ').title()}. "
                "Please try again."
            )
            agent_response_event = {
                "content": {"parts": [{"text": fallback_text}], "role": "model"},
                "author": app_name,
                "id": str(uuid.uuid4()),
                "timestamp": time.time(),
            }
            processed_response.append(agent_response_event)

        return jsonify(processed_response)

    except requests.RequestException as e:
        logger.error(f"Error in run_chat: {e}")
        # Fallback to simulated response
        simulated_response_text = f"Error connecting to backend. Simulated response from {app_name.replace('_', ' ').title()}. You said: '{new_message.get('parts', [{}])[0].get('text', '')}'"
        agent_response_event = {
            "content": {"parts": [{"text": simulated_response_text}], "role": "model"},
            "author": app_name,
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
        }
        return jsonify([agent_response_event])


@app.route("/apps/<app_name>/users/<user_id>/sessions", methods=["GET"])
@login_required
def list_user_sessions(app_name, user_id):
    """Lists all chat sessions for a given user and agent using the backend API."""
    # Check authorization - compare with current session user
    if str(user_id) != str(session.get("user_id")):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Call the backend API
        logger.info(f"Fetching sessions for user {user_id} and app {app_name}")
        response = requests.get(
            f"{API_URL}/apps/{app_name}/users/{user_id}/sessions", timeout=10
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        logger.error(f"Error fetching sessions: {e}")
        # Return empty list in case of error
        return jsonify([]), 500


@app.route("/apps/<app_name>/users/<user_id>/sessions/<session_uuid>", methods=["GET"])
@login_required
def get_session_history(app_name, user_id, session_uuid):
    """Retrieves the full event history for a specific chat session from the backend API."""
    if str(user_id) != str(session.get("user_id")):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Call the backend API to get session details
        logger.info(f"Fetching history for session {session_uuid} (app: {app_name}, user: {user_id})")
        response = requests.get(
            f"{API_URL}/apps/{app_name}/users/{user_id}/sessions/{session_uuid}",
            timeout=10,
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        logger.error(f"Error fetching session history: {e}")
        return jsonify({"error": f"Error retrieving session: {str(e)}"}), 500


@app.route("/apps/<app_name>/users/<user_id>/sessions/<session_uuid>", methods=["POST"])
@login_required
def create_or_update_session(app_name, user_id, session_uuid):
    """Creates or updates a session in the backend API."""
    if str(user_id) != str(session.get("user_id")):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Get the state data from the request
        state_data = request.json
        logger.info(f"Creating/updating session {session_uuid} for app {app_name} and user {user_id}")

        # Forward the request to the backend API
        response = requests.post(
            f"{API_URL}/apps/{app_name}/users/{user_id}/sessions/{session_uuid}",
            json=state_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        # Check if the session already exists
        if response.status_code == 200:
            logger.info(f"Successfully created/updated session {session_uuid}")
            return jsonify(response.json())
        elif "already exists" in response.text:
            logger.info(f"Session {session_uuid} already exists")
            return jsonify({"detail": f"Session already exists: {session_uuid}"}), 409
        else:
            response.raise_for_status()
            return jsonify(response.json())

    except requests.RequestException as e:
        logger.error(f"Error creating/updating session: {e}")
        return jsonify({"error": f"Error with session operation: {str(e)}"}), 500


@app.route("/agent-info", methods=["GET"])
@login_required
def get_agent_info():
    """Returns the agent information from environment variable."""
    logger.info("Serving agent information")
    return jsonify(AGENT_INFO)


if __name__ == "__main__":
    logger.info("Starting Flask application on port 8080")
    app.run(port=int(os.getenv("PORT", "8080")), host="0.0.0.0")
