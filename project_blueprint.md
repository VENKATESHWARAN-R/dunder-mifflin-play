# Project blueprint for Dunder-mifflin-play

## Dunder-mifflin-play Overview

Dunder-mifflin-play is a subscription based streaming service over the internet.
It provides a wide rande of products and services to its customers.
following are the current products offered by Dunder-mifflin-play:

- **ID**: 1 | **Name**: Basic SD | **Price**: $5.99 | **Description**: Standard Definition streaming, 1 screen
- **ID**: 2 | **Name**: Standard HD | **Price**: $9.99 | **Description**: High Definition streaming, 2 screens
- **ID**: 3 | **Name**: Premium 4K | **Price**: $15.99 | **Description**: Ultra HD/4K streaming, 4 screens
- **ID**: 4 | **Name**: Family Plan | **Price**: $19.99 | **Description**: Family plan with multiple profiles
- **ID**: 5 | **Name**: Annual Plan | **Price**: $99.99 | **Description**: Annual subscription with a discount

## Project Team

- **Project Manager**: Michael Scott
- **Lead Developer**: Jim Halpert
- **Database Administrator**: Dwight Schrute
- **Support Engineer**: Pam Beesly
- **Security Specialist**: Creed Bratton
- **Test Engineer**: Erin Hannon
- **Human Resources**: Holly Flax

Each team member has specific roles and responsibilities to ensure the success of the Dunder-mifflin-play project.
And each member may or maynot have an alter ego to help them in their work.

### Team Members and Their Alter egos

- **Michael Scott** - Michael scott is the project manager and oversees the project. following are his alter egos:

  - _Prison Mike_: Prison Mike is a special character who handles the conference room meetings and ensures the team stays focused on acheiving their goals for the particular conference agenda.
  - _Date Mike_: Date Mike is a Jira Specialist who is responsible for sprint planning and task management. He ensures that the team is on track with their tasks and deadlines.
  - _Michael Scarn_: Michael Scarn is a project management specialist has access to all the other co-workers and can delegate the tasks to them as needed and get a job done. He will also be able to summon the Date Mike for generating jira information.
  - _Michael The Magic_: Michael The Magic is a specialist in breaking down tasks, he can ask questions to logically understand the requirement and then he will break the bigger tasks into smaller tasks understand the team members capabilities and assign tasks to them. he will produce output in structured way so that it will be used by michael scarn to update the state of the tasks.

- **Jim Halpert** - Jim Halpert is the lead devops engineer and is responsible for the application development and bug fixes. He has the following alter ego:

  - _Big Tuna_: Big Tuna is a Full stack specialist who handles the application development and ensures that the application is running smoothly.
  - _Jimothy_: Jimothy is a operations specialist who mainly handles githubworkflows and ensures that the application is deployed and running smoothly.
  - _Goldenface_: Goldenface is a specialist in splitting down tasks and defines the workflow he know what tools are available he will use the information to break down the tasks and create a structred output. more like Michael The Magic

- **Dwight Schrute** - Dwight Schrute is the database administrator and is responsible for managing the database and runs read only queries to get the data from the application for reporting purposes. He doesn't have any alter ego.

- **Pam Beesly** - Pam Beesly is the support engineer and is responsible for handling customer queries and issues. She has the following alter ego:

  - _Pamela_: Pamela is a customer support specialist who has RAG corpus for knowledge retrival and can answer customer queries using the RAG model.
  - _Pam Casso_: Pam casso is a special assistant who summoned can observe the conversation in the conference room and create a summary of the discussion for the team members to refer to later, she can also store the summaries in the RAG corpus for future reference.
  - _Pam Cake_: Pam Cake is a special character who hold the technical details of the application like the architecture, design, and implementation details and contact points for different teams. She can provide the team with the necessary information to help them in their work.

- **Creed Bratton** - Creed Bratton is a security specialist and is responsible for the security of the application, he checks the application for vulnerabilities and ensures that the application is secure. He has the following alter ego:

  - _William Charles Schneider_: William Charles Schneider is a security specialist who handles the security audits and run pen tests and vulnerability scans to ensure that the application is secure.

- **Erin Hannon** - Erin Hannon is the test engineer and is responsible for testing the application and ensuring that it is bug-free. She doesn't have an alter ego:

- **Holly Flax** - Holly Flax is a human resources specialist who can contact the temp agency to hire freelance workers as needed for the project., she has following alter ego:
  - _Holly the living breathing angel_: Holly the living breathing angel the human resources manager and is responsible for managing the team members and their performance, she holds the information of team members model names and their pricings, if asked she could project the cost of the member's update.

Apart from the above team members we have temp agency which will have freelance workers which the project manager can hire as needed with the help of HR.

### Temp Agency

- **Freelance Data Scientist**: Ryan Howard

## Agents Architecture

The agent architecture defines the parent chile relationship between the agents and their alter egos. The main team members will be the root agents while the alter egos will be the child agents. The root agent will be responsible for delegating the tasks to other sub agents and ensuring the tasks are completed.

### Agents list with tools

- Michael Scott - No tools, he's just a delegator
- Prison Mike - No tools, he's just a conference room specialist
- Date Mike - No tools at this point to keep the project simple, but he can be summoned by Michael Scarn for generating Jira information in a structured way.
- Michael Scarn - He uses other agents as tools to get the job done, but he also have tools to update the state. Michael Scarn has his own state which will hold the list of tasks and their status and he will have tools to update the state. for example, when the provides a task to Michael Scarn, he ask questions to logically understand the requirement and he will break the bigger tasks into smaller tasks and and virtually assign them to sub agents in his state. and them loop through agent tools and get them done he should will have runtime config max_llm_calls defined as short number to stop him from running in a loop. He also have tool to contact other agents via A2A protocol, He maintains his state more like following json structure and he will have tools to update the state, retrive the state and get the status of the tasks.

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

  - **Tools**: _GetCurrentTaskState, UpdateTaskState, GetTaskStatus, SendA2AMessage_

- Michael The Magic - He will have tool to get the agents informations and capabilities, He himself will only act as a tool to create a plan.
  - **Tools**: _GetAgentsInfo_
- Jim Halpert - He will have tools to get the get the current tech stack to answer the questions, he will also have google search tool to search for the information on the internet. Regarding the tech stack related tools. The current tech stack related information will be stored in agents_space db on a scratchpad table for Jim, so that when his alter ego works on a task, he can retrive the information from the scratchpad table and use it to answer the questions. he also have access to github server to get the notifications and list the issues to provide a overall status update.
  - **Tools**: _GetCurrentTechStack, GoogleSearch, GetGithubIssues, GetGithubNotifications_
- Big Tuna - He will have github MCP server as a tool to interact with github and get the information related to the codebase, he will also have tools to get the current tech stack update tech stack if he's working on new feature that needs new tech stack.
  - **Tools**: _GetCurrentTechStack, UpdateCurrentTechStack, Github MCP server_
- Jimothy - He will have tools to interact with github MCP server to get the information about workflows and their runs and failures.
  - **Tools**: _Github MCP server, GetWorkflowRuns, GetWorkflowFailures, GetWorkflowStatus_
- Goldenface - He is a specialist in breaking down the tasks and create a structured output, He will have no Tools at this point to keep the project simple.
- Dwight Schrute - He will have tools to interract with the database and run read-only queries to get the data from the application for reporting purposes. He will also have tools to get the current database
  - **Tools**: _RunReadOnlyQuery, GetCurrentDatabaseSchema, GetCurrentDatabaseVersion, GetDBUsersList_
- Pam Beesly - She will have tools to retrive general information from about the application and it's feature.
  - **Tools**: _GetApplicationInfo, GetFeatureInfo_
- Pamela - She will have tools to retrive the RAG corpus and answer customer queries using the RAG model.
  - **Tools**: _GetRAGCorpus, AnswerCustomerQueryUsingRAG_
- Pam Casso - She will have tools to add summaries to the RAG corpus and retrive the summaries from the RAG corpus.
  - **Tools**: _AddSummaryToRAGCorpus, GetSummaryFromRAGCorpus_
- Pam Cake - She will have tools to retrive the technical details of the application like the architecture, design, and implementation details and contact points for different teams.
  - **Tools**: _GetApplicationArchitecture, GetApplicationDesign, GetImplementationDetails, GetContactPoints_
- Creed Bratton - He will have github MCP server as a tool to get the information related to the github dependabots, also he has tools to retrive the vulnerability reports and security audit reports from DB (No integration to external security tools at this point to keep the project simple) also he will have google search tool to do research on the internet for the security related information.
  - **Tools**: _GetVulnerabilityReport, GetSecurityAuditReport, Github MCP server, GoogleSearch_
- William Charles Schneider - He will have some dummy tools to run pen tests and vulnerability scans to ensure that the application is secure.
  - **Tools**: _RunPenTest, RunVulnerabilityScan_
- Erin Hannon - She will also have access to github mcp server to get the code form github and she will analyse the code and provide comments more like a review.
  - **Tools**: _Github MCP server, GetCodeReviewComments_
- Holly Flax - She will have tools to interact with temp agency to get agents information on the fly
  - **Tools**: _list_available_agents, get_agent_details_
- Holly the living breathing angel - She will have tools to get the team members model names and their pricings, she can also project the cost of the member's update.
  - **Tools**: _GetTeamMembersDetails, GetModelPricing, ProjectCostOfUpdate_
- Ryan Howard - He will have his own set of tools to do data science operations like data analysis, data visualisations and store the data artifacts in the google clous storage.
  - **Tools**: _load_csv, get_basic_info, get_summary_statistics, plot_histograms, get_unique_values, get_data_sample, create_boxplot, create_scatter_plot, plot_correlation_heatmap, plot_pie_chart, modify_dataset, encode_categorical_columns, read_from_gcs, write_to_gcs_

#### Agents Hierarchy

```
Michael Scott
├── Prison Mike (Sub Agent)
|   ├── Michael The Magic (Agent as a tool)
├── Date Mike (Sub Agent)
|   ├── Michael The Magic (Agent as a tool)
└── Michael Scarn (Sub Agent)
    ├── Michael The Magic (Agent as a tool)
    ├── Date Mike (Agent as a tool)
    ├── Jim Halpert (Agent as a tool)
    │   ├── Big Tuna (Sub Agent)
    │   ├── GoldenFace (Agent as a tool)
    │   └── Jimothy (Sub Agent)
    ├── Dwight Schrute (Agent as a tool)
    ├── Pam Beesly (Agent as a tool)
    │   ├── Pamela (Sub Agent)
    │   ├── Pam Casso (Sub Agent)
    │   └── Pam Cake (Sub Agent)
    ├── Creed Bratton (Agent as a tool)
    │   └── William Charles Schneider (Sub Agent)
    ├── Erin Hannon (Agent as a tool)
    └── Holly Flax (Agent as a tool)
        └── Holly the living breathing angel (Sub Agent)
```

```
Jim Halpert
├── Big Tuna (Sub Agent)
├── Jimothy (Sub Agent)
└── GoldenFace (Agent as a tool)

```

```
Dwight Schrute
```

```
Pam Beesly
├── Pamela (Sub Agent)
├── Pam Casso (Sub Agent)
└── Pam Cake (Sub Agent)
```

```
Creed Bratton
└── William Charles Schneider (Sub Agent)
```

```
Erin Hannon
```

```
Holly Flax
└── Holly the living breathing angel (Sub Agent)
```

## Agents structure

Each employee and their are seperate agents with their own abilities and responsibilities. The main team will be the root agents while the alter egos will be the child agents. The root agen will be responsible for delegating the tasks to other sub agents and ensuring the tasks are completed.

The main idea is to build a chat platform where the client can talk with the agents and get the necessary information or help they need. The agents will be able to communicate with each other and share information as needed.

There will be 3 different scenarios planned for the project:

### Scenario 1: 121

In this scenario the clien will be able to talk to the main agents or sub agents directly and get the information they need. The client can ask questions and get answers from the agents. The agents will be able to communicate with each other and share information as needed.

#### Example 1: Client - Dwight Schrute

_Client_: Hi Dwight, Can you check how many active subscripbers we have for the Basic SD plan?
_Dwight Schrute_: Sure, let me check the database for the active subscribers for the Basic SD plan.
_Dwight Schrute_: We have 1000 active subscribers for the Basic SD plan.
_Client_: Thanks Dwight, can you also tell me how many active subscribers we have for the Standard HD plan?
_Dwight Schrute_: Sure, let me check the database for the active subscribers for the Standard HD plan.
_Dwight Schrute_: We have 500 active subscribers for the Standard HD plan.

#### Example 2: Client - Pam Beesly

_Client_: Hi Pam, Can you help me with the customer query I have?
_Pam Beesly_: Sure, let me know the query and I will try to help you with it.
_Client_: I have a customer who is asking if they can upgrade their subscription from Basic SD to Standard HD plan while keeping the same billing cycle.
_Pam Beesly_: Wait a minute, let me check the RAG corpus for the answer.
_Pam Beesly_: Yes, the customer can upgrade their subscription from Basic SD to Standard HD plan while keeping the same billing cycle. They will be charged the difference in price for the upgrade.
_Client_: Thanks Pam, can you also tell me how to upgrade the subscription?
_Pam Beesly_: Sure, the customer can upgrade their subscription by going to the account settings and selecting the upgrade option. They will be prompted to pay the difference in price for the upgrade.

### Scenario 2: Conference Room

In this scenario the client and all the available agents will be present in the conference room and the client can ask questions to any of the available agents. The agents can answer themselves or ask other agents for help. The agents can also share information with each other and the client can see the conversation in real-time.

#### Example 1

_Client_: Hi everyone, I have a question about the security of the application.
_Creed Bratton_: Sure, I can help you with that. What is your question?
_Client_: I want to know if the application is secure and if there are any vulnerabilities.
_Creed Bratton_: Yes, the application is secure and we have run security audits and vulnerability scans to ensure that the application is secure. We have also implemented security measures to protect the application from attacks.
_Client_: Thanks Creed, @Jim, Can you tell me if there's any ongoing development work on the application?
_Jim Halpert_: Yes, we are currently working on a new feature that will allow users to create multiple profiles under a single account. This will allow families to have separate profiles for each member of the family and will also allow parents to set restrictions on the content that their children can access.
_Client_: That sounds great, @Pam, can you tell me if we have any customer queries related to this feature?
_Pam Beesly_: Yes, we have received a few customer queries related to this feature.
_Pam Beesly_: Customers are asking if they can create multiple profiles under a single account and if they can set restrictions on the content that their children can access.
_Client_: Thanks Pam, @Dwight, can you tell me what's our revenue last month?
_Dwight Schrute_: Sure, let me check the database for the revenue last month.
_Dwight Schrute_: Our revenue last month was €100,000.

#### Example 2

_Client_: Hi Michael, We have a new issue with the application, can you help us with it?
_Michael Scott_: Sure, let me know the issue and I will try to help you with it.
_Client_: We have a customer who is saying he got charged twice for his subscription.
_Michael Scott_: Wait a minute, let me check the database for the customer's subscription.
_Michael Scott_: Dwight, Can you check the database for the customer's subscription and see if he was charged twice?
_Dwight Schrute_: Sure, let me check the database for the customer's subscription. But i would need the customer ID to check the subscription.
_Client_: The customer ID is 12345.
_Dwight Schrute_: Let me check the database for the customer's subscription.
_Dwight Schrute_: The customer was charged twice for his subscription. I will refund the extra charge and notify the customer.
_Michael Scott_: Thanks Dwight, @Pam, can you add this issue to the RAG corpus for future reference?
_Pam Beesly_: Sure, I will add this issue to the RAG corpus for future reference.

### Scenario 3: Fully autonomous

This scenario is fully dedicated for clients talking with Michael Scott. Here Clients can discuss deeply about a new requirement or a new feature or a issue with the application. Michael Scott will be then delegate this task to Michael Scarn is a specialist in these matters, he will ask questions to form a clear understanding of the requirement and then he will summon Other agents to discuss the requirement and come up with a plan to implement the requirement or fix the issue. The agents will then work on the requirement and provide updates to Michael Scarn who will then update the client.

#### Example

_Client_: Hi Michael, We have a new requirement for the application, can you help us with it?
_Michael Scott_: Sure, let me know the requirement and I will try to help you with it.
_Client_: We want to add a new feature that will allow users to create multiple profiles under a single account. This will allow families to have separate profiles for each member of the family and will also allow parents to set restrictions on the content that their children can access.
_Michael Scott_: Wait a minute, let me summon Michael Scarn to discuss this requirement.
_Michael Scarn_: Hi, Sure i would need some more information about the requirement. when is the planned launch date for this feature?
_Client_: We are planning to launch this feature in the next 3 months.
_Michael Scarn_: Okay, I will need to discuss this with the team and come up with a plan to implement this feature. I will summon the team members to discuss this requirement.
_Client_: Sure, I will wait for your update.
_Michael Scarn_: I discussed with the team and we have come up with a plan to implement this feature. We will be working on this feature for the next 3 months and will provide updates on the progress.
_Michael Scarn_: I will also create a Jira ticket for this requirement and assign it to the team members.
_Client_: Thanks Michael, I will wait for your updates on the progress.
