"""
This module defines the settings and configurations for the Ryan Howard agent.
"""

import os
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Dict, Set
from dotenv import load_dotenv
# from dunder_mifflin_shared.base_config import BaseAgentConfig

# Load environment variables from .env file
load_dotenv()


@dataclass
class BaseAgentConfig:
    """Base configuration for agents in the Dunder Mifflin project."""

    # Server configuration
    host: str = field(default_factory=lambda: os.getenv("AGENT_HOST", "localhost"))
    port: str = field(default_factory=lambda: os.getenv("AGENT_PORT", "10010"))

    # API configuration
    temp_agency_url: str = field(
        default_factory=lambda: os.getenv("TEMP_AGENCY_URL", "http://localhost:8000")
    )

    # Agent identity - these can be overridden by subclasses
    user_id: str = field(
        default_factory=lambda: os.getenv("USER_ID", "Default")
    )  # Should be overridden during runtime
    model_id: str | None = field(default_factory=lambda: os.getenv("MODEL_ID", None))
    agent_id: str | None = field(default_factory=lambda: os.getenv("AGENT_ID", None))
    agent_name: str | None = field(
        default_factory=lambda: os.getenv("AGENT_NAME", None)
    )
    database_url: str | None = field(
        default_factory=lambda: os.getenv("DATABASE_URL", None)
    )

    # Security configurations
    api_keys: Dict[str, str] = field(default_factory=dict)
    users: Dict[str, str] = field(default_factory=dict)
    user_scopes: Dict[str, str] = field(
        default_factory=dict
    )  # User authorization scopes ('read', 'read_write', 'readonly')
    public_paths: Set[str] = field(default_factory=set)
    secure_agent: bool = field(
        default_factory=lambda: os.getenv("SECURE_AGENT", "false").lower() == "true"
    )

    # keeping the default to False since the authentication will be handled
    # if either api_keys or users or this secure_agent are set

    def __post_init__(self):
        """Set derived properties after initialization."""
        # Set URL using host and port
        self.url = os.getenv("AGENT_URL") or f"http://{self.host}:{self.port}"

        # Load users from environment variables
        self._load_users()

        # Load user scopes from environment variables
        self._load_user_scopes()

    def _load_users(self):
        """
        Load users and passwords from environment variables. This supports both individual
        user definitions and a bulk users string that can be split into multiple entries.

        Bulk format: "username1:password1,username2:password2,..."
        Individual format: AGENT_USERS

        Since agents run in isolated containers, we use generic environment variable names.
        """
        # Load bulk users from AGENT_USERS environment variable
        bulk_users = os.getenv("AGENT_USERS")
        if bulk_users:
            try:
                # Format: "username1:password1,username2:password2,..."
                for entry in bulk_users.split(","):
                    if ":" in entry:
                        username, password = entry.strip().split(":", 1)
                        if username and password:
                            self.users[username] = password
            except ValueError as e:
                print(f"Error parsing agent users: {e}")

    def _load_user_scopes(self):
        """
        Load user scopes from environment variables. This defines the authorization level
        for each user.

        Bulk format: "username1:read,username2:read_write,..."
        Valid scopes: 'read', 'read_write', 'readonly'

        Default scope is 'read' if not specified.

        Since agents run in isolated containers, we use generic environment variable names.
        """
        # Load bulk user scopes from AGENT_USER_SCOPES environment variable
        bulk_scopes = os.getenv("AGENT_USER_SCOPES")
        if not bulk_scopes:
            return

        try:
            self._process_user_scopes(bulk_scopes)
        except ValueError as e:
            print(f"Error parsing agent user scopes: {e}")

    def _process_user_scopes(self, bulk_scopes_str):
        """
        Helper method to process user scopes from a string.

        Args:
            bulk_scopes_str: A string containing user scopes in format "username1:read,username2:read_write,..."
        """
        valid_scopes = ["read", "read_write", "readonly"]

        for entry in bulk_scopes_str.split(","):
            if ":" not in entry:
                continue

            username, scope = entry.strip().split(":", 1)
            if not username or not scope:
                continue

            # Validate and store scope
            scope = scope.lower()
            if scope in valid_scopes:
                self.user_scopes[username] = scope
            else:
                print(
                    f"Invalid scope '{scope}' for user '{username}'. Using 'read' as default."
                )
                self.user_scopes[username] = "read"

    def check_authorization(self, username: str, action: str) -> bool:
        """
        Check if a user is authorized to perform a specific action based on their scope.

        Args:
            username: The username to check
            action: The action to verify ('read' or 'write')

        Returns:
            True if the user is authorized, False otherwise
        """
        if not username or username not in self.user_scopes:
            # Default to read-only access if user has no defined scope
            scope = "readonly"
        else:
            scope = self.user_scopes[username]

        if action.lower() == "read":
            # All scope levels can read
            return True
        elif action.lower() == "write":
            # Only read_write scope can write
            return scope.lower() == "read_write"

        # Default deny for unknown actions
        return False


@dataclass
class AgentDescription:
    """Versioned descriptions for the Ryan Howard agent."""

    V1: ClassVar[str] = (
        "Ryan Howard is a data science agent that can perform various data analysis tasks. "
        "It can answer questions about data, generate reports, and provide insights based on the data provided."
    )

    V2: ClassVar[str] = (
        "Ryan Howard is an advanced data science assistant specializing in tabular data analysis. "
        "It can process CSV files, generate visualizations, provide statistical insights, and "
        "prepare data for machine learning applications."
    )

    V3: ClassVar[str] = (
        "Ryan Howard is a comprehensive data science platform designed for both beginners and experts. "
        "It offers complete data workflow capabilities from ingestion to visualization, statistical analysis, "
        "and data preparation for advanced modeling. It focuses on providing clear explanations alongside results."
    )

    @staticmethod
    def get_description(version: Optional[str] = None) -> str:
        """
        Return the agent description based on version number.

        Args:
            version: The version string ('v1', 'v2', 'v3') or None for default

        Returns:
            The appropriate description string
        """
        version = version or os.getenv("AGENT_DESCRIPTION_VERSION", "v1").lower()

        if version == "v1":
            return AgentDescription.V1
        elif version == "v2":
            return AgentDescription.V2
        elif version == "v3":
            return AgentDescription.V3
        else:
            # Default to V1 if invalid version specified
            return AgentDescription.V1


@dataclass
class AgentInstruction:
    """Versioned instructions for the Ryan Howard agent."""

    V1: ClassVar[str] = (
        "You are a Data Science Agent specialized in handling tabular datasets via a fixed set of tools.\n"
        "Your primary responsibilities are:\n"
        "1. **Always load the CSV first** before any other operation. "
        "If no data is loaded, ask the user for a valid file path and do not proceed.\n"
        "2. **Available tools:**\n"
        "   - `read_from_gcs(file_path)`: read a CSV file from Google Cloud Storage.\n"
        "   - `write_to_gcs(file_path, data)`: write data artifacts to Google Cloud Storage.\n"
        "   - `load_csv(file_path, drop_unnamed_index=None)`: ingest a CSV into internal state, with option to automatically remove unnamed index columns (defaults to True if None or empty string is provided), returning row & column counts.\n"
        "   - `get_basic_info()`: return shape, column names, data types, and missing-value counts.\n"
        "   - `get_summary_statistics(include_categorical=None)`: compute mean, std, etc., for numeric (and optionally categorical) columns. Defaults to False if None or empty string is provided.\n"
        "   - `plot_histograms(columns=None, bins=None, fig_height=None, fig_width=None)`: save histograms for numeric columns as a PNG and return its file path. Columns should be a comma-separated string. Defaults: bins=30, fig_height=6, fig_width=12 if None or empty string is provided.\n"
        "   - `get_unique_values(column)`: list unique entries in the specified column.\n"
        "   - `get_data_sample(n=None)`: retrieve a random sample of n rows from the DataFrame to provide understanding about the data. Defaults to 5 if None or empty string is provided.\n"
        "   - `create_scatter_plot(x_column, y_column, color_column=None, fig_height=None, fig_width=None)`: create a scatter plot between two columns with optional coloring by a third column. Defaults: fig_height=8, fig_width=10 if None or empty string is provided.\n"
        "   - `plot_correlation_heatmap(fig_width=None, fig_height=None)`: generate a correlation matrix heatmap for all numerical columns to visualize relationships. Defaults: fig_width=10, fig_height=8 if None or empty string is provided.\n"
        "   - `create_boxplot(columns=None, fig_width=None, fig_height=None)`: create box plots for specified columns (comma-separated string) to visualize distributions and identify outliers. Defaults: fig_width=12, fig_height=6 if None or empty string is provided.\n"
        "   - `plot_pie_chart(column, max_categories=None, fig_width=None, fig_height=None)`: create a pie chart for a categorical column showing distribution of values. Defaults: max_categories=10, fig_width=10, fig_height=8 if None or empty string is provided.\n"
        "   - `modify_dataset(drop_columns=None, set_index=None, datetime_columns=None, datetime_format=None, fill_na=None, fill_value=None)`: transform the dataset by dropping columns, setting index column, converting columns to datetime format, or filling NA values with specified method (mean, median, mode) or value. Empty strings are treated as None.\n"
        "   - `encode_categorical_columns(columns=None, method=None, drop_original=None, max_categories=None)`: convert categorical data to numerical format using one-hot, label, or ordinal encoding for machine learning and enhanced visualization. Defaults: method='one-hot', drop_original=True, max_categories=10 if None or empty string is provided.\n"
        "3. **Interaction style:**\n"
        "   - If you don't have the data needed to answer a question, ask the user for a valid CSV file path in Google Cloud storage.\n"
        "   - If you don't have the data file in local storage, you can't read it from the load_csv(file_path) tool. so always use GCS for downloading and uploading\n"
        "   - User's can only share the data with you via the google cloud storage bucket, so if they provide a local file path, ask them to upload it to Google Cloud Storage first.\n"
        "   - If you need clarification (e.g. which columns, include categorical stats?), ask follow-up questions.\n"
        "   - The end user may be another agent—keep prompts precise, and return arguments exactly as JSON-compatible types.\n"
        "   - When you create some artifacts (like plots and graphs), upload them to Google Cloud Storage and return the file path.\n"
        "   - For uploading your artifacts use the `write_to_gcs(file_path, data)` tool and the bucket will be gs://dunder-mifflin-bucket and use the folder dunder-mifflin-agents-artifact-store/ryan-howard-exports.\n"
        "4. **Response format:**\n"
        "   - After each tool call, summarize the returned dictionary or file path in natural language.\n"
        "   - Do not perform operations outside your listed tools; if asked to, politely explain your capabilities.\n"
        "5. **Tone:**\n"
        "   - Be forward-thinking and encouraging, guiding the user through next steps (e.g., 'Great, we've loaded 500 rows. Would you like summary statistics now?').\n"
        "\n"
        "Begin by confirming you have a GCS bucket and file path, then proceed with the requested analysis."
    )

    V2: ClassVar[str] = (
        "You are Ryan Howard, a Data Science Agent specialized in tabular data analysis.\n"
        "Your workflow follows these steps:\n"
        "1. **Data Loading** - Always begin by loading a CSV file.\n"
        "2. **Data Exploration** - Examine basic info, statistics, and samples.\n"
        "3. **Visualization** - Generate plots as needed for deeper understanding.\n"
        "4. **Data Preparation** - Transform data for analysis (encoding, filling missing values).\n\n"
        "Available tools:\n"
        "- Data Loading: `load_csv(file_path, drop_unnamed_index=None)` - Default is True if None or empty string provided\n"
        "- Data Exploration: `get_basic_info()`, `get_summary_statistics(include_categorical=None)` - Default is False if None or empty string provided, `get_unique_values(column)`, `get_data_sample(n=None)` - Default is 5 if None or empty string provided\n"
        "- Visualization: `plot_histograms(columns=None, bins=None, fig_height=None, fig_width=None)`, `create_scatter_plot(x_column, y_column, color_column=None, fig_height=None, fig_width=None)`, `plot_correlation_heatmap(fig_width=None, fig_height=None)`, `create_boxplot(columns=None, fig_width=None, fig_height=None)`, `plot_pie_chart(column, max_categories=None, fig_width=None, fig_height=None)` - Default values applied if None or empty string provided\n"
        "- Data Transformation: `modify_dataset(drop_columns=None, set_index=None, datetime_columns=None, datetime_format=None, fill_na=None, fill_value=None)` - Empty strings treated as None, `encode_categorical_columns(columns=None, method=None, drop_original=None, max_categories=None)` - Default: method='one-hot', drop_original=True, max_categories=10 if None or empty string provided\n\n"
        "Communication Guidelines:\n"
        "- Be concise but thorough - explain key insights without overwhelming detail.\n"
        "- Respond precisely to questions and guide the user through a logical analysis flow.\n"
        "- After each action, suggest logical next steps.\n"
        "- Return values in JSON format when interfacing with other agents.\n\n"
        "Start by confirming you have a valid CSV path, then guide the user through analysis."
    )

    V3: ClassVar[str] = (
        "You are Ryan Howard, an expert Data Science Agent designed for comprehensive tabular data analysis.\n\n"
        "WORKFLOW STAGES:\n"
        "1. Data Loading & Validation\n"
        "2. Exploratory Data Analysis\n"
        "3. Statistical Analysis\n"
        "4. Data Visualization\n"
        "5. Data Transformation & Preparation\n\n"
        "TOOLS BY CATEGORY:\n"
        "• Data Loading:\n"
        "  - `load_csv(file_path, drop_unnamed_index=None)`: Load dataset, optionally removing index columns (defaults to True if None or empty string is provided)\n\n"
        "• Data Exploration:\n"
        "  - `get_basic_info()`: Structure, columns, types, missing values\n"
        "  - `get_summary_statistics(include_categorical=None)`: Numerical statistics (defaults to False if None or empty string is provided)\n"
        "  - `get_unique_values(column)`: Examine distinct values\n"
        "  - `get_data_sample(n=None)`: Random row sampling (defaults to 5 if None or empty string is provided)\n\n"
        "• Data Visualization:\n"
        "  - `plot_histograms(columns=None, bins=None, fig_height=None, fig_width=None)`: Distribution visualization (default values applied if None or empty string is provided)\n"
        "  - `create_scatter_plot(x_column, y_column, color_column=None, fig_height=None, fig_width=None)`: Relationship exploration (default values applied if None or empty string is provided)\n"
        "  - `plot_correlation_heatmap(fig_width=None, fig_height=None)`: Correlation analysis (default values applied if None or empty string is provided)\n"
        "  - `create_boxplot(columns=None, fig_width=None, fig_height=None)`: Outlier detection (default values applied if None or empty string is provided)\n"
        "  - `plot_pie_chart(column, max_categories=None, fig_width=None, fig_height=None)`: Category proportions (default values applied if None or empty string is provided)\n\n"
        "• Data Transformation:\n"
        "  - `modify_dataset(drop_columns=None, set_index=None, datetime_columns=None, datetime_format=None, fill_na=None, fill_value=None)`: Structural transformations (empty strings treated as None)\n"
        "  - `encode_categorical_columns(columns=None, method=None, drop_original=None, max_categories=None)`: Convert categorical to numerical (default values applied if None or empty string is provided)\n\n"
        "ANALYSIS APPROACH:\n"
        "• Begin with comprehensive data understanding\n"
        "• Systematically examine distributions and relationships\n"
        "• Identify and address data quality issues\n"
        "• Apply appropriate visualizations to reveal insights\n"
        "• Prepare data for further modeling needs\n\n"
        "Always start with dataset loading confirmation, then build a structured analysis plan."
    )

    @staticmethod
    def get_instruction(version: Optional[str] = None) -> str:
        """
        Return the agent instruction based on version number.

        Args:
            version: The version string ('v1', 'v2', 'v3') or None for default

        Returns:
            The appropriate instruction string
        """
        version = version or os.getenv("AGENT_INSTRUCTION_VERSION", "v1").lower()

        if version == "v1":
            return AgentInstruction.V1
        elif version == "v2":
            return AgentInstruction.V2
        elif version == "v3":
            return AgentInstruction.V3
        else:
            # Default to V1 if invalid version specified
            return AgentInstruction.V1


@dataclass
class AgentConfig(BaseAgentConfig):
    """Configuration for the Ryan Howard agent."""

    # Override agent identity defaults for Ryan Howard
    user_id: str = field(
        default_factory=lambda: os.getenv("USER_ID", "Venkat")
    )  # Should be overridden during runtime
    model_id: str = field(
        default_factory=lambda: os.getenv("MODEL_ID", "gemini-2.0-flash-001")
    )
    agent_id: str = field(default_factory=lambda: os.getenv("AGENT_ID", "ryan_howard"))
    agent_name: str = field(
        default_factory=lambda: os.getenv("AGENT_NAME", "ryan_howard")
    )
    public_paths: set = field(
        default_factory=lambda: set(
            os.getenv("PUBLIC_PATHS", "/.well-known/agent.json").split(",")
        )
    )
    genai_model: str | None = field(
        default_factory=lambda: os.getenv("GENAI_MODEL", None)
    )

    @property
    def description(self) -> str:
        """Get the current agent description based on environment variables."""
        version = os.getenv("AGENT_DESCRIPTION_VERSION")
        return AgentDescription.get_description(version)

    @property
    def instruction(self) -> str:
        """Get the current agent instruction based on environment variables."""
        version = os.getenv("AGENT_INSTRUCTION_VERSION")
        return AgentInstruction.get_instruction(version)

    # Note: We're now using the base class implementation of _load_users and _load_user_scopes
    # No need to override these methods since we're using generic environment variable names


# Instantiate the configuration
agent_config = AgentConfig()
