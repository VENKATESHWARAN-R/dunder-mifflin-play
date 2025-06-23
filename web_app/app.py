# app.py
import os
import uuid
import json
import psycopg2
import time
from datetime import datetime
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


# --- Database Connection ---
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to database: {e}")
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
        "conference_room", "creed_bratton", "dwight_schrute", "erin_hannon", 
        "holly_flax", "jim_halpert", "michael_scott", "pam_beesly"
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
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
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
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
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
    return render_template("home.html", username=session.get("username"))


# @app.route("/chat/<agent_name>")
# @login_required
# def chat_page(agent_name):
#     """Renders the dedicated chat page for a specific agent."""
#     # Validate agent_name if necessary
#     agent_list, _ = get_list_apps()
#     if agent_name not in agent_list.get_json():
#         flash("Invalid agent selected.", "danger")
#         return redirect(url_for("home"))

#     return render_template(
#         "chat.html", agent_name=agent_name, username=session.get("username")
#     )

@app.route('/chat/<agent_name>')
@login_required
def chat_page(agent_name):
    """Renders the dedicated chat page for a specific agent."""
    # CORRECTED VALIDATION: Call the helper function to get a plain list
    valid_agents = _get_agent_list()
    if agent_name not in valid_agents:
        flash("Invalid agent selected.", "danger")
        return redirect(url_for('home'))
        
    return render_template('chat.html', agent_name=agent_name, username=session.get('username'))


# --- Simulated External API Endpoints ---


# @app.route("/list-apps", methods=["GET"])
# @login_required
# def get_list_apps():
#     """Simulated endpoint to list available chat agents."""
#     agents = [
#         "conference_room",
#         "creed_bratton",
#         "dwight_schrute",
#         "erin_hannon",
#         "holly_flax",
#         "jim_halpert",
#         "michael_scott",
#         "pam_beesly",
#     ]
#     return jsonify(agents)

@app.route('/list-apps', methods=['GET'])
@login_required
def get_list_apps():
    """Simulated endpoint to list available chat agents."""
    # CORRECTED: This route now also uses the helper function
    agents = _get_agent_list()
    return jsonify(agents)

@app.route("/run", methods=["POST"])
@login_required
def run_chat():
    """
    Simulated endpoint to process a chat message and return a response.
    This also handles creating and updating chat sessions in the database.
    """
    data = request.json
    app_name = data.get("app_name")
    user_id = session.get("user_id")
    session_id = data.get("session_id")
    new_message = data.get("new_message")

    if not all([app_name, user_id, session_id, new_message]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Check if session exists
    cur.execute("SELECT * FROM chat_sessions WHERE session_id = %s", (session_id,))
    chat_session = cur.fetchone()

    # Append new user message
    db_events = []
    if chat_session:
        db_events = chat_session.get("events", [])

    db_events.append(new_message)

    # Simulate agent response
    simulated_response_text = f"This is a simulated response from {app_name.replace('_', ' ').title()}. You said: '{new_message['parts'][0]['text']}'"
    agent_response_event = {
        "content": {"parts": [{"text": simulated_response_text}], "role": "model"},
        "author": app_name,
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
    }
    db_events.append(agent_response_event)

    # Upsert session data
    if chat_session:
        cur.execute(
            """
            UPDATE chat_sessions 
            SET events = %s, last_update_time = CURRENT_TIMESTAMP
            WHERE session_id = %s
            """,
            (json.dumps(db_events), session_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO chat_sessions (session_id, user_id, app_name, events) 
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, user_id, app_name, json.dumps(db_events)),
        )
    conn.commit()
    cur.close()
    conn.close()

    # Return only the new agent response as per the requirement
    return jsonify([agent_response_event])


@app.route("/apps/<app_name>/users/<int:user_id>/sessions", methods=["GET"])
@login_required
def list_user_sessions(app_name, user_id):
    """Lists all chat sessions for a given user and agent."""
    if user_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT 
            session_id as id, 
            app_name as "appName", 
            user_id as "userId",
            last_update_time as "lastUpdateTime"
        FROM chat_sessions 
        WHERE user_id = %s AND app_name = %s
        ORDER BY last_update_time DESC
        """,
        (user_id, app_name),
    )
    sessions = cur.fetchall()
    cur.close()
    conn.close()

    # Add empty state and events fields as required
    for s in sessions:
        s["state"] = {}
        s["events"] = []

    return jsonify(sessions)


@app.route(
    "/apps/<app_name>/users/<int:user_id>/sessions/<session_uuid>", methods=["GET"]
)
@login_required
def get_session_history(app_name, user_id, session_uuid):
    """Retrieves the full event history for a specific chat session."""
    if user_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT 
            session_id as id, 
            app_name as "appName", 
            user_id as "userId",
            events,
            last_update_time as "lastUpdateTime"
        FROM chat_sessions 
        WHERE session_id = %s AND user_id = %s AND app_name = %s
        """,
        (session_uuid, user_id, app_name),
    )
    chat_session = cur.fetchone()
    cur.close()
    conn.close()

    if not chat_session:
        return jsonify({"error": "Session not found"}), 404

    chat_session["state"] = {}  # Add empty state field
    return jsonify(chat_session)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
