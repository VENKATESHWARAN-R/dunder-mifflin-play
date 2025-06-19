# Plan for the Project

## Done So far

1. At this point i have the ryan and temp agency and holly ready to go
2. Ryan and temp agency is already deployed to the cloud Run
3. The dunder-mifflin-play application is also deployed to cloud run and has it's own database setup in the cloud SQL

## Next Steps

1. **Create a Common MCP server**
    - Set up a common MCP server to handle requests from all agents.
    - Ensure it can route requests to the appropriate agent based on the request type.
    - Deploy it in Cloud Run.
  
2. **Build other agents and sub agents**
    - Implement the remaining agents and their sub-agents:
        - Michael Scott and his sub-agents (Prison Mike, Date Mike, Michael Scarn)
        - Jim Halpert and his sub-agents (Big Tuna, Jimothy)
        - Dwight Schrute
        - Pam Beesly and her sub-agents (Pamela, Pam Casso, Pam Cake)
        - Creed Bratton and his sub-agent (William Charles Schneider)
        - Erin Hannon
        - Holly Flax and her sub-agent (Holly the Living Breathing Angel)
3. **Integrate Agents with MCP Server**
    - Each agent should be able to communicate with the MCP server.
    - Implement the necessary APIs for each agent to handle requests and responses.
4. **Modify prompts and configurations**
    - Update the prompts and configurations for each agent to ensure they are tailored to their specific roles.
    - Ensure that the prompts are consistent with the overall theme of the Dunder Mifflin universe.
