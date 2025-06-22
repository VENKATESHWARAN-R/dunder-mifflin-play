# Ryan Howard Agent

## Overview

Ryan Howard is a data science agent that can perform various data analysis tasks. It can answer questions about data, generate reports, and provide insights based on the data provided.

## Features

- Load and inspect CSV files
- Generate basic info and summary statistics about datasets
- Create visualizations such as histograms
- Retrieve unique values from columns
- Auto-registers with the Temp Agency service on startup
- Auto-deregisters from the Temp Agency service on shutdown

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) or pip for package management

## Installation

Clone the repository and install the dependencies:

```bash
# Using uv
uv sync

# Or using pip
pip install -e .
```

## Configuration

The agent configuration is stored in `config.py` and inherits from the shared `BaseAgentConfig` class:

### Environment Variables

- `AGENT_HOST`: Host address where the agent will run (default: "localhost")
- `AGENT_PORT`: Port number for the agent (default: 10010)
- `TEMP_AGENCY_URL`: URL of the Temp Agency registry service (default: "http://localhost:8000")
- `USER_ID`: ID of the user interacting with the agent (default: "Venkat")
- `MODEL_ID`: ID of the model powering the agent (default: "gemini-2.0-flash-001")
- `AGENT_ID`: ID of this agent (default: "ryan_howard")
- `AGENT_NAME`: Display name of this agent (default: "Ryan_Howard")
- `AGENT_DESCRIPTION_VERSION`: Version of agent description to use (v1, v2, v3)
- `AGENT_INSTRUCTION_VERSION`: Version of agent instructions to use (v1, v2, v3)
- `SECURE_AGENT`: Enable authentication (default: "false")
- `PUBLIC_PATHS`: Comma-separated list of public paths that do not require authentication (default: "/.well-known/agent.json,/openapi.json,/docs,/redoc")

### Authentication

When `SECURE_AGENT=true`, the agent requires authentication. Configure users with:

- `AGENT_USERS`: Comma-separated list of username:password pairs (e.g., "admin:password,user1:password1")
- `AGENT_USER_SCOPES`: Comma-separated list of username:scope pairs (e.g., "admin:read_write,user1:read")

Valid scopes are:

- `read`: Can read data but not modify it
- `read_write`: Can both read and modify data
- `readonly`: Can only read data (most restrictive)

You can set these environment variables in a `.env` file or pass them when running the agent.

## Running the Agent

### Direct Execution

Run the agent from agents directory:

```bash
cd /path/to/project-dunder-mifflin/scranton/agents
uvicorn ryan_howard.a2a_server:app --host localhost --port 10010 --reload
```

The agent will:

1. Start up at the configured host and port
2. Register itself with the Temp Agency service
3. Begin serving requests
4. Deregister itself when shut down (use CTRL+C)

### Package Import

You can also import and use the agent in your own Python code:

```python
from ryan_howard.agent import RayanHowardAgent

agent = RayanHowardAgent()
response = await agent.handle_query("Can you help me analyze this CSV file?", "session_id")
```

## API Usage

Once the agent is running, you can interact with it through its HTTP API:

- **Base URL**: `http://localhost:10010` (or as configured)
- **Agent description**: `GET /.well-known/agent.json`

### Example API Calls

#### Get Agent Details

```bash
curl -s \
  http://localhost:10010/.well-known/agent.json
```

#### Send Non-Streaming Message (Without Authentication)

```bash
curl -s -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":"1",
    "method":"message/send",
    "params":{
      "message":{
        "role":"user",
        "parts":[
          {"kind":"text","text":"Hi there! what can you do?"}
        ],
        "messageId":"msg-1"
      }
    }
  }'
```

#### Send Streaming Message (Without Authentication)

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":"2",
    "method":"message/stream",
    "params":{
      "message":{
        "role":"user",
        "parts":[
          {"kind":"text","text":"I want you to analyse this CSV file for me and provide insights, please."}
        ],
        "messageId":"msg-99"
      }
    }
  }'
```

#### Send Non-Streaming Message (With Basic Authentication)

When `SECURE_AGENT=true`, you need to include authentication:

```bash
curl -s -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
    "jsonrpc":"2.0",
    "id":"1",
    "method":"message/send",
    "params":{
      "message":{
        "role":"user",
        "parts":[
          {"kind":"text","text":"Hi there! what can you do?"}
        ],
        "messageId":"msg-1"
      }
    }
  }'
```

#### Send Streaming Message (With Basic Authentication)

```bash
curl -N -X POST http://localhost:10010/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:password' | base64)" \
  -d '{
    "jsonrpc":"2.0",
    "id":"2",
    "method":"message/stream",
    "params":{
      "message":{
        "role":"user",
        "parts":[
          {"kind":"text","text":"I want you to analyse this CSV file for me and provide insights, please."}
        ],
        "messageId":"msg-99"
      }
    }
  }'
```

> **Note**: The host (`localhost`) and port (`10010`) in these examples may change depending on your configuration in `config.py` or environment variables.

## Development

To extend or modify this agent, you can add new data science tools in the `tools/data_science_tools.py` file.

## Troubleshooting

### Registration Failures

If the agent fails to register with the Temp Agency, ensure that:

- The Temp Agency service is running at the configured URL
- The agent has network access to the Temp Agency
- The agent URL is correctly configured and accessible from the Temp Agency

## License

This project is licensed under the terms specified in the repository's LICENSE file.
