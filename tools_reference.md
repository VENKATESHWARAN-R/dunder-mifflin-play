# Dunder-Mifflin-Play: Tools Reference

This document provides a comprehensive reference of all tools mentioned in the project blueprint, organized by agent. This reference can be used for building an MCP server implementation.

## Michael Scott's Tools

Michael Scott primarily acts as a delegator and doesn't have specific tools assigned to him.

## Prison Mike's Tools

Prison Mike is a conference room specialist who handles meetings and doesn't have specific tools assigned to him.

## Date Mike's Tools

Date Mike is a Jira Specialist responsible for sprint planning and task management. Currently, Date Mike doesn't have specific tools assigned to keep the project simple, but can be summoned by Michael Scarn for generating Jira information in a structured way.

## Michael Scarn's Tools

Michael Scarn uses other agents as tools and has specific tools to manage tasks and state:

| Tool | Description |
|------|-------------|
| `GetCurrentTaskState` | Retrieves the current state of tasks being managed |
| `UpdateTaskState` | Updates the state of tasks in the system |
| `GetTaskStatus` | Gets the current status of a specific task |
| `SendA2AMessage` | Facilitates Agent-to-Agent communication via protocol |

Michael Scarn maintains state in the following structure:

```json
{
  "task_id": "12345",
  "task_name": "Implement new feature",
  "status": "in_progress",
  "sub_tasks": [
    {
      "sub_task_id": "12345-1",
      "sub_task_name": "Design the feature",
      "assigned_to": "Jim Halpert",
      "status": "not_started"
    },
    {
      "sub_task_id": "12345-2",
      "sub_task_name": "Implement the feature",
      "assigned_to": "Jim Halpert",
      "status": "not_started"
    }
  ]
}
```

## Michael The Magic's Tools

Michael The Magic helps in understanding tasks and breaking them down into manageable parts. He uses the following tools:

| Tool | Description |
|------|-------------|
| `GetAgentsInfo` | Retrieves detailed information about all available agents |

## Jim Halpert's Tools

Jim Halpert is the lead DevOps engineer responsible for application development and bug fixes. He has the following tools:

| Tool | Description |
|------|-------------|
| `GetCurrentTechStack` | Retrieves information about the current technology stack |
| `GoogleSearch` | Searches the internet for information |
| `GetGithubIssues` | Gets issues from GitHub repositories |
| `GetGithubNotifications` | Retrieves notifications from GitHub |

## Big Tuna's Tools (Jim's alter ego)

Big Tuna is a full stack specialist handling application development. He has the following tools:

| Tool | Description |
|------|-------------|
| `GetCurrentTechStack` | Retrieves information about the current technology stack |
| `UpdateCurrentTechStack` | Updates the technology stack information when working with new features |
| `Github MCP server` | Interacts with GitHub to access codebase information |

## Jimothy's Tools (Jim's alter ego)

Jimothy is an operations specialist who mainly handles GitHub workflows. He has the following tools:

| Tool | Description |
|------|-------------|
| `Github MCP server` | Interacts with GitHub to access codebase information |
| `GetWorkflowRuns` | Retrieves information about workflow runs |
| `GetWorkflowFailures` | Gets information about workflow failures |
| `GetWorkflowStatus` | Checks the status of workflows |

## Goldenface's Tools (Jim's alter ego)

Goldenface is a specialist in breaking down tasks and defining workflows. He currently doesn't have specific tools assigned to keep the project simple.

## Dwight Schrute's Tools

Dwight Schrute is the database administrator responsible for managing the database and running read-only queries. He has the following tools:

| Tool | Description |
|------|-------------|
| `RunReadOnlyQuery` | Executes read-only queries on the database for reporting purposes |
| `GetCurrentDatabaseSchema` | Retrieves the current database schema |
| `GetCurrentDatabaseVersion` | Gets the current version of the database |
| `GetDBUsersList` | Lists all database users |

## Pam Beesly's Tools

Pam Beesly is the support engineer responsible for handling customer queries and issues. She has the following tools:

| Tool | Description |
|------|-------------|
| `GetApplicationInfo` | Retrieves general information about the application |
| `GetFeatureInfo` | Gets information about specific features |

## Pamela's Tools (Pam's alter ego)

Pamela is a customer support specialist who uses the RAG corpus for knowledge retrieval. She has the following tools:

| Tool | Description |
|------|-------------|
| `GetRAGCorpus` | Retrieves information from the RAG (Retrieval Augmented Generation) corpus |
| `AnswerCustomerQueryUsingRAG` | Answers customer queries using the RAG model |

## Pam Casso's Tools (Pam's alter ego)

Pam Casso observes conversations in the conference room and creates summaries. She has the following tools:

| Tool | Description |
|------|-------------|
| `AddSummaryToRAGCorpus` | Adds summaries to the RAG corpus for future reference |
| `GetSummaryFromRAGCorpus` | Retrieves summaries from the RAG corpus |

## Pam Cake's Tools (Pam's alter ego)

Pam Cake holds the technical details of the application. She has the following tools:

| Tool | Description |
|------|-------------|
| `GetApplicationArchitecture` | Retrieves information about the application architecture |
| `GetApplicationDesign` | Gets information about the application design |
| `GetImplementationDetails` | Retrieves information about implementation details |
| `GetContactPoints` | Gets contact points for different teams |

## Creed Bratton's Tools

Creed Bratton is the security specialist responsible for checking application vulnerabilities. He has the following tools:

| Tool | Description |
|------|-------------|
| `GetVulnerabilityReport` | Retrieves vulnerability reports from the database |
| `GetSecurityAuditReport` | Gets security audit reports from the database |
| `Github MCP server` | Accesses GitHub for dependabot information |
| `GoogleSearch` | Searches the internet for security-related information |

## William Charles Schneider's Tools (Creed's alter ego)

William Charles Schneider is a security specialist handling security audits and tests. He has the following tools:

| Tool | Description |
|------|-------------|
| `RunPenTest` | Runs penetration tests on the application |
| `RunVulnerabilityScan` | Executes vulnerability scans on the application |

## Erin Hannon's Tools

Erin Hannon is the test engineer responsible for testing the application. She has the following tools:

| Tool | Description |
|------|-------------|
| `Github MCP server` | Accesses code from GitHub for review |
| `GetCodeReviewComments` | Retrieves code review comments |

## Holly Flax's Tools

Holly Flax is the human resources specialist who contacts the temp agency for freelance workers. She has the following tools:

| Tool | Description |
|------|-------------|
| `list_available_agents` | Lists all available agents in the temp agency |
| `get_agent_details` | Gets details about specific agents |

## Holly the living breathing angel's Tools (Holly's alter ego)

Holly the living breathing angel manages team members and their performance. She has the following tools:

| Tool | Description |
|------|-------------|
| `GetTeamMembersDetails` | Retrieves details about team members |
| `GetModelPricing` | Gets pricing information for models |
| `ProjectCostOfUpdate` | Projects the cost of updates |

## Ryan Howard's Tools (Freelance Data Scientist)

Ryan Howard is a freelance data scientist available through the temp agency. He has the following tools:

| Tool | Description |
|------|-------------|
| `load_csv` | Loads CSV data for analysis |
| `get_basic_info` | Gets basic information about datasets |
| `get_summary_statistics` | Retrieves summary statistics for data |
| `plot_histograms` | Creates histogram visualizations |
| `get_unique_values` | Gets unique values from datasets |
| `get_data_sample` | Retrieves sample data from datasets |
| `create_boxplot` | Creates boxplot visualizations |
| `create_scatter_plot` | Creates scatter plot visualizations |
| `plot_correlation_heatmap` | Creates correlation heatmap visualizations |
| `plot_pie_chart` | Creates pie chart visualizations |
| `modify_dataset` | Modifies datasets |
| `encode_categorical_columns` | Encodes categorical columns in datasets |
| `read_from_gcs` | Reads data from Google Cloud Storage |
| `write_to_gcs` | Writes data to Google Cloud Storage |

## MCP Server Implementation Considerations

When implementing these tools in your MCP server:

1. Define clear interfaces for each tool with appropriate input parameters and return types
2. For tools that maintain state (like Michael Scarn's task management tools), design a suitable state management system
3. Implement authentication and authorization for agent-to-agent communication
4. Design database connectors for tools that interact with databases
5. Implement appropriate security measures for tools that execute queries or code
6. Consider rate limiting for external API calls (Google Search, GitHub)
7. Implement logging for all tool operations for debugging and auditing
