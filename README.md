# Dunder Mifflin Play

A multi-agent system built with Google's Agent Development Kit (ADK) that simulates "The Office" TV show characters working together on a subscription-based streaming service. This project demonstrates the power of agent-based systems where each character has specialized roles and capabilities.

## Project Setup

### Prerequisites

- Docker
- Python 3.12+
- Google Cloud CLI (optional, for cloud deployment)

### Local Setup

1. **Install dependencies using UV**:

   ```bash
   uv sync
   ```

2. **Start the MCP Server**:

   ```bash
   # Build MCP server image
   docker build -t dunder-mifflin-mcp-server:latest ./dunder_mifflin_mcp

   # Run MCP server
   docker run -p 8080:8080 dunder-mifflin-mcp-server:latest
   ```

3. **Start the Temp Agency**:

   ```bash
   # Build temp agency image
   docker build -t temp-agency:latest ./temp_agency/app

   # Run temp agency
   docker run -p 8000:8000 temp-agency:latest
   ```

4. **Start Ryan Howard's Agent**:

   ```bash
   # Build Ryan's agent image
   docker build -t ryan-howard:latest ./temp_agency/ryan_howard

   # Run Ryan's agent
   docker run ryan-howard:latest
   ```

5. **Start Scranton Agents**:

   ```bash
   # Build Scranton agents image
   cd ./scranton/agents
   docker build -t dunder-mifflin-agents:latest .

   # Run agents
   docker run dunder-mifflin-agents:latest
   ```

### Required Environment Variables

The following environment variables are needed when running agents locally:

```bash
SUBSCRIPTION_DB_URL=postgresql://username:password@hostname:port/dbname
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
GOOGLE_API_KEY=your_google_api_key
GITHUB_PAT_TOKEN=your_github_pat_token
APP_DATABASE_URL=postgresql://username:password@hostname:port/dbname
MCP_SERVER_URL=http://localhost:8080
```

> Note: Some agents like Pam (RAG operations) and Dwight (database operations) require additional setup for full functionality.

## Multi-Agent Architecture

The Dunder Mifflin Play project blends characters from "The Office" TV show into an IT organization supporting a streaming service application. Each character is implemented as an autonomous AI agent with unique roles, tools, and expertise.

### Agent Communication Modes

#### 1. Individual Agents

Each agent operates as an individual unit capable of performing specialized tasks. You can interact with them one-on-one to leverage their specific expertise:

- **Michael Scott**: Project Manager who delegates tasks to other agents
- **Jim Halpert**: Lead DevOps Engineer handling development workloads using GitHub's MCP server
- **Dwight Schrute**: Database Administrator connecting to databases and generating reports stored in GCS
- **Pam Beesly**: Support Engineer utilizing Vertex AI for RAG-based customer support
- **Creed Bratton**: Security Specialist handling vulnerability assessments
- **Erin Hannon**: Test Engineer working with GitHub's MCP server for testing
- **Holly Flax**: HR Representative who communicates with the Temp Agency

#### 2. Conference Room Mode

This mode enables all agents to collaborate on complex problems simultaneously. In Conference Room mode, agents can:

- Share information and discuss requirements
- Work together on solutions by leveraging each other's strengths
- Provide comprehensive answers to complex questions

### System Expandability

The project includes a "Temp Agency" model for dynamically adding new agents:

- **Temp Agency**: A FastAPI server that manages temporary staff agents
- **Ryan Howard**: An independent agent built with Google's Agent-to-Agent (A2A) protocol
- **A2A Integration**: Ryan registers himself with the Temp Agency when active and deregisters when shutting down
- **Dynamic Discovery**: Holly can contact the Temp Agency to find new talent and retrieve their contact information
- **Cross-Agent Communication**: Michael has tools to communicate with external agents like Ryan via the A2A protocol

### Agent Capabilities

The capabilities of agents can be explored in their respective `prompts.py` files in the `scranton/agents` directory. Each agent has:

- Specialized tools aligned with their role
- Unique personas (alter egos) for different capabilities
- Integration with external services (GitHub, databases, Vertex AI, etc.)

For more detailed information about agents, their tools, and personas, please refer to the [project blueprint](project_blueprint.md).
The project blueprint is the original draft, but at this point the project might have diverged from it a bit.
But the soul of the project remains the same

### Related Links

- [dunder-mifflin-office](https://dunder-mifflin-office-852224482282.europe-north1.run.app): The web interface for interacting with the agents
- [dunder-mifflin-play-app](https://github.com/VENKATESHWARAN-R/dunder-mifflin-play-app): The repository which contains the application code for the Dunder Mifflin Play project.
- [dunder-mifflin-agents](https://dunder-mifflin-agents-852224482282.europe-north1.run.app): The endpoint url where this project is deployed.
