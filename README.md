# dunder-mifflin-play
Repository for building multi Agent system with ADK

## For deploying agents to agent engine

List available agents:
```bash
python -m scripts.deploy_agent list
```

Deploy an agent:
```bash
python -m scripts.deploy_agent deploy --agent michael_scott
```

Test a deployed agent:
```bash
python -m scripts.deploy_agent test --resource-name <resource-name>
```

Delete a deployed agent:
```bash
python -m scripts.deploy_agent delete --resource-name <resource-name>
```

## Agent Configuration

Agent configurations are stored in `scripts/agent_config.json`. The configuration includes:

- `module_path`: Python import path to the agent module
- `display_name`: Human-readable name for the agent
- `description`: Description of the agent
- `gcs_dir_name`: Directory name in GCS for agent artifacts
- `requirements`: List of Python package requirements
- `env_vars`: Environment variables for the agent
- `parent_agent`: For personas, the main agent they belong to

To add a new agent or modify an existing one, update the `agent_config.json` file.

## For deploying mcp server to cloud run

## Available Agent Hierarchy

The system contains the following agents:

### Main Agents
- michael_scott: Michael Scott - Regional Manager of Dunder Mifflin Scranton Branch
- jim_halpert: Jim Halpert - Sales Representative 
- dwight_schrute: Dwight Schrute - Assistant to the Regional Manager
- pam_beesly: Pam Beesly - Office Administrator
- holly_flax: Holly Flax - Human Resources Representative
- ryan_howard: Ryan Howard - Temp turned VP of Sales
- creed_bratton: Creed Bratton - Quality Assurance
- erin_hannon: Erin Hannon - Receptionist

### Personas
- Michael's personas:
  - prison_mike: Prison Mike - Michael's prison alter ego
  - date_mike: Date Mike - Michael's dating alter ego
  - michael_scarn: Michael Scarn - Michael's action hero alter ego

- Jim's personas:
  - big_tuna: Big Tuna - Jim's nickname
  - golden_face: Golden Face - Jim's character in Threat Level Midnight
  - jimothy: Jimothy - Jim's formal alter ego

- Creed's personas:
  - william_charles_schneider: William Charles Schneider - Creed's identity for debt transfer

- Holly's personas:
  - holly_the_living_breathing_angel: Holly the Living Breathing Angel - Michael's loving nickname for Holly



