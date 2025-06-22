"""
Initialization module for Pam Beesly agent in the Scranton branch of Dunder Mifflin.
"""

import os

import vertexai
from dotenv import load_dotenv

from . import agent

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI with the project and location from environment variables
print("Initializing Vertex AI with project and location...")
if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")
if not os.getenv("GOOGLE_CLOUD_LOCATION"):
    print("GOOGLE_CLOUD_LOCATION not set, defaulting to 'europe-west3'.")
elif os.getenv("GOOGLE_CLOUD_LOCATION") != "europe-west3":
    print("GOOGLE_CLOUD_LOCATION is set to a non-default value, using it as provided.")
    os.environ["GOOGLE_CLOUD_LOCATION"] = "europe-west3"

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west3"),
)

__all__ = [
    "agent",
]
