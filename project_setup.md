# Project Setup Instructions

```bash
# Create the main directory structure
mkdir -p scranton/agents

# Helper function to create agent directories with required files
create_agent_dir() {
  local dir=$1
  mkdir -p "$dir"
  touch "$dir/__init__.py"
  touch "$dir/agent.py"
  touch "$dir/prompts.py"
  touch "$dir/config.py"
}

# Create main agents and their sub-agents
## Michael Scott and sub-agents
create_agent_dir "scranton/agents/michael_scott"
create_agent_dir "scranton/agents/michael_scott/prison_mike"
create_agent_dir "scranton/agents/michael_scott/date_mike"
create_agent_dir "scranton/agents/michael_scott/michael_scarn"

## Jim Halpert and sub-agents
create_agent_dir "scranton/agents/jim_halpert"
create_agent_dir "scranton/agents/jim_halpert/big_tuna"
create_agent_dir "scranton/agents/jim_halpert/jimothy"

## Dwight Schrute (no sub-agents)
create_agent_dir "scranton/agents/dwight_schrute"

## Pam Beesly and sub-agents
create_agent_dir "scranton/agents/pam_beesly"
create_agent_dir "scranton/agents/pam_beesly/pamela"
create_agent_dir "scranton/agents/pam_beesly/pam_casso"
create_agent_dir "scranton/agents/pam_beesly/pam_cake"

## Creed Bratton and sub-agent
create_agent_dir "scranton/agents/creed_bratton"
create_agent_dir "scranton/agents/creed_bratton/william_charles_schneider"

## Erin Hannon (no sub-agents)
create_agent_dir "scranton/agents/erin_hannon"

## Holly Flax and sub-agent
create_agent_dir "scranton/agents/holly_flax"
create_agent_dir "scranton/agents/holly_flax/holly_the_living_breathing_angel"

# Ryan Howard (contractor)
create_agent_dir "scranton/agents/ryan_howard"

# Create main package __init__.py
touch "scranton/__init__.py"
touch "scranton/agents/__init__.py"
```