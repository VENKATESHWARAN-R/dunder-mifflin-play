# Dunder Mifflin Play

A multi-agent system built with Google's Agent Development Kit (ADK) that simulates "The Office" TV show characters working together on a subscription-based streaming service. This project demonstrates the power of agent-based systems where each character has specialized roles and capabilities.

## Agent Architecture

The project is organized as a hierarchy of agents, each with specialized capabilities and tools. The agent hierarchy is visualized below:

### Agent Hierarchy Visualizations

| Agent | Role | Hierarchy Visualization |
|-------|------|-------------------------|
| Michael Scott | Project Manager | ![Michael Scott Agent Hierarchy](./architecture/agent-hierarchies/michael_scott.png) |
| Jim Halpert | Lead DevOps Engineer | ![Jim Halpert Agent Hierarchy](./architecture/agent-hierarchies/jim_halpert.png) |
| Dwight Schrute | Database Administrator | ![Dwight Schrute Agent Hierarchy](./architecture/agent-hierarchies/dwight_schrute.png) |
| Pam Beesly | Support Engineer | ![Pam Beesly Agent Hierarchy](./architecture/agent-hierarchies/pam_beesly.png) |
| Creed Bratton | Security Specialist | ![Creed Bratton Agent Hierarchy](./architecture/agent-hierarchies/creed_bratton.png) |
| Erin Hannon | Test Engineer | ![Erin Hannon Agent Hierarchy](./architecture/agent-hierarchies/erin_hannon.png) |
| Holly Flax | HR Representative | ![Holly Flax Agent Hierarchy](./architecture/agent-hierarchies/holly_flax.png) |
| Michael Scarn | Special Agent | ![Michael Scarn Agent Hierarchy](./architecture/agent-hierarchies/michael_scarn.png) |
| Conference Room | Collaboration Space | ![Conference Room Agent Hierarchy](./architecture/agent-hierarchies/conference_room.png) |

For detailed descriptions of each agent's role and capabilities, refer to the documentation in the [agent-hierarchies](./architecture/agent-hierarchies/) directory.

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

The Conference Room Orchestrator enables all agents to collaborate on complex problems simultaneously. This agent:

- Facilitates communication between multiple specialized agents in a group setting
- Delegates questions to the appropriate team member based on their expertise
- Never provides direct answers, focusing solely on routing inquiries to the right agent
- Maintains awareness of the team structure and each member's specialized knowledge
- Creates a collaborative environment where agents can share information and work together
- Defaults to Michael Scott for questions that don't clearly fit one agent's domain
- Enables seamless transitions between agents when complex problems require multiple perspectives

#### 3. Michael Scarn: Executive Boss Agent

Michael Scarn serves as the main user-facing agent with these capabilities:

- Operates as a comprehensive gateway agent that can access all specialized team members
- Answers questions directly when possible but consults with specialized agents when needed
- Maintains awareness of each team member's expertise and delegates accordingly
- Uses specialized tools to communicate with Michael Scott, Dwight Schrute, Creed Bratton, Holly Flax, Pam Beesly, and Erin Hannon
- Follows a structured delegation workflow, telling users which agent he's consulting
- Integrates responses from specialized agents into comprehensive answers
- Presents expert insights in a conversational, user-friendly manner
- References his secret agent alter-ego occasionally with playful confidence
- Serves as a one-stop interface for accessing the entire team's combined knowledge

### Agent Hierarchy

The Dunder-Mifflin-Play project features a hierarchical organization of agents with parent agents and their specialized sub-agents:

#### Root-Level Agents

1. **Michael Scott**: Project Manager overseeing the entire project and team coordination
2. **Jim Halpert**: Lead DevOps Engineer for application development and technical infrastructure
3. **Dwight Schrute**: Database Administrator managing customer and subscription data
4. **Pam Beesly**: Support Engineer handling customer queries and documentation
5. **Creed Bratton**: Security Specialist monitoring vulnerabilities and platform security
6. **Erin Hannon**: Test Engineer ensuring application quality and bug-free code
7. **Holly Flax**: HR Specialist handling temp recruitment and team structure
8. **Michael Scarn**: Executive Boss Agent serving as main user-facing gateway
9. **Conference Room**: Collaborative orchestrator for multi-agent discussions

#### Sub-Agents

- **Michael Scott's Sub-Agents**:
  - *Michael The Magic*: Requirements Analysis Specialist breaking down complex tasks into detailed plans
  - *Date Mike*: Jira Specialist converting plans into structured tickets with estimates

- **Jim Halpert's Sub-Agents**:
  - *Big Tuna*: Full Stack Specialist handling application development
  - *Jimothy*: Operations Specialist managing GitHub workflows and deployments
  - *Goldenface*: Task Breakdown Specialist organizing technical requirements into implementation plans

- **Pam Beesly's Sub-Agents**:
  - *Pamela*: Primary RAG Search Agent retrieving information from knowledge corpus
  - *Pam Casso*: Meeting Documentation Specialist creating conversation summaries
  - *Pam Cake*: Application Architecture Specialist providing technical details

- **Creed Bratton's Sub-Agents**:
  - *William Charles Schneider*: Security Audit Specialist performing penetration tests and vulnerability scans

- **Holly Flax's Sub-Agents**:
  - *Holly the Living Breathing Angel*: Team Member Models Specialist tracking pricing and projecting staffing costs

#### External/Temp Agency Agents

- **Ryan Howard**: Data Scientist available through the Temp Agency for specialized data tasks

### System Expandability

The project includes a "Temp Agency" model for dynamically adding new agents:

- **Temp Agency**: A FastAPI server that manages temporary staff agents
- **Ryan Howard**: An independent agent built with Google's Agent-to-Agent (A2A) protocol
- **A2A Integration**: Ryan registers himself with the Temp Agency when active and deregisters when shutting down
- **Dynamic Discovery**: Holly can contact the Temp Agency to find new talent and retrieve their contact information
- **Cross-Agent Communication**: Michael has tools to communicate with external agents like Ryan via the A2A protocol

## Screenshots

### Web Interface

The Dunder Mifflin Play system includes a web interface for interacting with the agents:

![Home Page](./architecture/screenshots/home_page.png)

### Agent Conversations

Examples of conversations with different agents in the system:

#### Michael Scott (Project Manager)

![Michael Scott Conversation](./architecture/screenshots/michael_scott.png)

#### Michael Scott using Agent-to-Agent Communication

![Michael Scott A2A](./architecture/screenshots/michael_scott_a2a.png)

#### Michael Scarn (Executive Boss Agent)

![Michael Scarn Conversation](./architecture/screenshots/michael_scarn.png)

#### Conference Room Mode

![Conference Room Conversation](./architecture/screenshots/conference-room.png)

## Agent Capabilities

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
