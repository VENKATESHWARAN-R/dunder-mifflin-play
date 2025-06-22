# Temp Agency

This service acts as a registry for freelance agents in the Dunder Mifflin application ecosystem. It allows agents to register themselves by providing their Agent Card, making them discoverable by other agents or services within the system.

## Project Structure

The application follows a modular structure for better maintainability and readability:

```
/temp_agency
  ├── .env              # Environment variables
  ├── app/              # Application package
  │   ├── api/          # API endpoints organized by resource
  │   ├── db/           # Database connections and operations
  │   ├── models/       # Data models and schemas
  │   ├── services/     # Business logic 
  │   ├── config.py     # Configuration management
  │   └── main.py       # FastAPI application definition
  ├── main.py           # Entry point for the service
  ├── README.md         # This file
  └── pyproject.toml    # Project dependencies
```

## Running the Service

From the project root directory:

```bash
# Make sure Postgres DB is running
docker run -d --name temp-agency -p 5432:5432 -e POSTGRES_USER=temp_admin -e POSTGRES_PASSWORD=temp_password -e POSTGRES_DB=temp_agency_db postgres:latest
#docker run -d --name holly-mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=hollyadmin -e MONGO_INITDB_ROOT_PASSWORD=secret mongo:latest

# Start the Temp Agency service
cd temp_agency
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Or simply run:

```bash
python main.py
```

## Environment Variables

The application uses the following environment variables that can be set in the `.env` file:

```
# Database Configuration
DATABASE_URL=postgresql://temp_admin:temp_password@localhost:5432/temp_agency_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
RELOAD=true
WORKERS=1

# Application Settings
PUBLIC_AGENT_CARD_PATH=/.well-known/agent.json
```

## Features

- Agent registration via Agent Card with name uniqueness constraint
- Agent discovery by URL or name with health status information
- Listing of all registered agents
- Agent deregistration by URL or name
- Health check endpoint

## Technology Stack

- FastAPI - API framework
- MongoDB - Database for agent registry
- httpx - HTTP client for async operations
- a2a-sdk - Agent-to-Agent communication library

## API Endpoints

### Register an Agent

```
POST /register_agent/
```

Request body:
```json
{
  "agent_service_url": "http://agent-service-url"
}
```

Notes:
- Each agent must have a unique name and URL
- If an agent with the same URL already exists, its information will be updated
- If an agent with the same name but different URL tries to register, a 409 Conflict error will be returned

### List All Agents

```
GET /agents/?skip=0&limit=10
```

### Get Agent by Name

```
GET /agents/by-name/{agent_name}
```

Response includes agent information plus health status:
```json
{
  "name": "Agent Name",
  "url": "http://agent-service-url",
  "health": {
    "is_online": true,
    "last_checked": "2025-06-03 14:23:45 UTC",
    "response_time_ms": 245.67
  },
  ...other agent properties
}
```

### Get Agent by URL

```
GET /agents/by-url?url=http://agent-service-url
```

Response includes agent information plus health status (same format as above).

### Deregister Agent by URL

```
DELETE /deregister_agent/by-url?url=http://agent-service-url
```

### Deregister Agent by Name

```
DELETE /deregister_agent/by-name/{agent_name}
```

### Health Check

```
GET /health
```

## Local Development

### Running with Docker

```bash
docker build -t temp-agency .
docker run -p 8000:8000 temp-agency
```

## Uniqueness Constraints

The Temp Agency service enforces two uniqueness constraints:

1. **URL Uniqueness**: Each agent must have a unique URL.
   - If an agent attempts to register with a URL that already exists, the existing record will be updated.
   - This allows agents to update their information while keeping their URL as a consistent identifier.

2. **Name Uniqueness**: Each agent must have a unique name.
   - If an agent attempts to register with a name that's already used by a different URL, registration will fail.
   - This prevents confusion from having multiple agents with the same name.

### Registration Scenarios

Here's what happens in different registration scenarios:

1. **Same Agent Re-registering (Same URL)**:
   - The existing record is updated with any new information.
   - Status: 200 OK with success message.

2. **Same Agent Re-registering (Different URL but Same Name)**:
   - Registration fails with a 409 Conflict error.
   - The agent would need to use a different name or deregister the old entry first.

3. **Different Agent with Same Name**:
   - Registration fails with a 409 Conflict error.
   - Agent names must be unique across all agents.

4. **New Agent with Unique Name and URL**:
   - Registration succeeds.
   - Status: 200 OK with success message.

## Health Checks

All endpoints that return agent information include a health check. The health check verifies:

- If the agent is online (can be reached)
- Response time
- Time of last check

This ensures that consumers of the API can see the current status of agents before attempting to use them.