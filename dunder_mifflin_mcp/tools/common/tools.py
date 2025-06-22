"""
This moudle will contain common tools used by the agents in the Dunder Mifflin MCP project.
"""


def get_project_tech_stack():
    """
    Get information about the project's technology stack.

    This function analyzes the project structure and returns a dictionary with details
    about the frontend, backend, database, and infrastructure technologies used in the
    Dunder Mifflin Play application.

    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if information was retrieved successfully, 'error' otherwise
            - message (str): A message describing the result of the operation
            - result (dict): A dictionary with tech stack details organized by category
    """
    try:
        # Create the result dictionary with tech stack information
        result = {
            "frontend": {
                "technologies": [
                    {
                        "name": "HTML5/CSS3/JavaScript",
                        "description": "Vanilla frontend technologies used for building the UI",
                    },
                    {
                        "name": "Nginx",
                        "description": "Web server used to serve static frontend files",
                    },
                ],
                "architecture": "Simple static web application served by Nginx",
            },
            "backend": {
                "languages": [
                    {
                        "name": "Python 3.9+",
                        "description": "Core programming language used for the backend",
                    }
                ],
                "frameworks": [
                    {
                        "name": "Flask",
                        "description": "Web framework for building the RESTful API",
                    }
                ],
                "libraries": [
                    {
                        "name": "SQLAlchemy",
                        "description": "ORM library for database interactions",
                    },
                    {
                        "name": "psycopg2",
                        "description": "PostgreSQL adapter for Python",
                    },
                    {
                        "name": "Faker",
                        "description": "Library used for generating test data",
                    },
                    {
                        "name": "python-dotenv",
                        "description": "Library for loading environment variables from .env files",
                    },
                    {
                        "name": "gunicorn",
                        "description": "WSGI HTTP server for running the Flask application in production",
                    },
                    {
                        "name": "flask-cors",
                        "description": "Extension for handling Cross-Origin Resource Sharing",
                    },
                ],
            },
            "database": {
                "type": "PostgreSQL",
                "description": "Relational database used for storing application data",
                "orm": "SQLAlchemy",
                "cloud_service": "Google Cloud SQL",
            },
            "infrastructure": {
                "cloud_provider": "Google Cloud Platform (GCP)",
                "services": [
                    {
                        "name": "Google Cloud Run",
                        "description": "Serverless platform for deploying and scaling containerized applications",
                    },
                    {
                        "name": "Google Cloud SQL",
                        "description": "Fully managed relational database service for PostgreSQL",
                    },
                    {
                        "name": "Google Artifact Registry",
                        "description": "Container registry for storing and managing Docker images",
                    },
                ],
                "containerization": [
                    {
                        "name": "Docker",
                        "description": "Container platform used for packaging the application",
                    },
                    {
                        "name": "Docker Compose",
                        "description": "Tool for defining and running multi-container applications locally",
                    },
                ],
            },
            "ci_cd": {"deployment": "Custom deployment scripts for Cloud Run services"},
        }

        return {
            "status": "success",
            "message": "Project technology stack information retrieved successfully",
            "result": result,
        }
    except (RuntimeError, IOError) as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve project technology stack information: {str(e)}",
            "result": {},
        }



def get_application_architecture():
    """
    Get detailed information about the application architecture, data flow, and GCP implementation.
    
    This function returns a structured dictionary containing information about the application's
    architecture, data flow, and how it is implemented in Google Cloud Platform (GCP).
    
    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if information was retrieved successfully, 'error' otherwise
            - message (str): A message describing the result of the operation
            - result (dict): A dictionary with architecture, data flow, and GCP implementation details
    """
    try:
        # Create the result dictionary with architecture information
        result = {
            "application_architecture": {
                "pattern": "Microservice architecture",
                "components": {
                    "frontend": {
                        "description": "Static web application serving HTML, CSS, and JavaScript files",
                        "container": "Nginx-based Docker container",
                        "key_files": [
                            "index.html - Main application entry point",
                            "script.js - Client-side JavaScript for API interaction",
                            "style.css - Styling for the application"
                        ]
                    },
                    "backend": {
                        "description": "RESTful API service built with Python Flask",
                        "container": "Python-based Docker container with Gunicorn WSGI server",
                        "key_components": [
                            "app.py - Main Flask application entry point",
                            "models.py - SQLAlchemy ORM models defining data entities",
                            "database.py - Database connection and session management",
                            "routes/ - API endpoints organized with Flask Blueprints"
                        ]
                    },
                    "database": {
                        "description": "PostgreSQL relational database",
                        "deployment": "Cloud SQL managed PostgreSQL instance",
                        "schema": {
                            "tables": [
                                "users - Stores user account information",
                                "subscriptions - Stores available subscription plans",
                                "user_subscriptions - Tracks user subscription history and status"
                            ]
                        }
                    }
                }
            },
            "data_flow": {
                "user_interaction": {
                    "description": "User interaction flow with the application",
                    "flow": [
                        "User accesses the frontend application served by Cloud Run",
                        "Frontend makes API requests to the backend service for data",
                        "Backend processes requests, interacts with the PostgreSQL database",
                        "Database returns relevant data to the backend",
                        "Backend formats response and sends it to the frontend",
                        "Frontend renders data for the user"
                    ]
                },
                "api_flows": [
                    {
                        "name": "List Users",
                        "endpoint": "GET /api/users",
                        "flow": [
                            "Frontend makes GET request to backend",
                            "Backend queries database for all users",
                            "Database returns user records",
                            "Backend formats and returns JSON response"
                        ]
                    },
                    {
                        "name": "View User Subscriptions",
                        "endpoint": "GET /api/users/{user_id}/subscriptions",
                        "flow": [
                            "Frontend makes GET request with user ID",
                            "Backend validates user exists",
                            "Backend queries database for user's subscriptions",
                            "Database returns subscription records",
                            "Backend formats and returns JSON response"
                        ]
                    },
                    {
                        "name": "Add Subscription",
                        "endpoint": "POST /api/users/{user_id}/subscriptions",
                        "flow": [
                            "Frontend sends POST request with user ID and subscription details",
                            "Backend validates user and subscription exist",
                            "Backend creates new user_subscription record in database",
                            "Database confirms successful creation",
                            "Backend returns success confirmation with new subscription details"
                        ]
                    }
                ]
            },
            "gcp_implementation": {
                "services": {
                    "compute": {
                        "service": "Cloud Run",
                        "description": "Serverless platform for deploying containerized applications",
                        "components": [
                            {
                                "name": "Frontend Service",
                                "configuration": {
                                    "container": "Nginx with static files",
                                    "cpu": "0.5 CPU",
                                    "memory": "256 MB",
                                    "scaling": "Auto-scaling from 1 to 10 instances",
                                    "environment_variables": {
                                        "API_BASE_URL": "URL to the backend service"
                                    }
                                }
                            },
                            {
                                "name": "Backend Service",
                                "configuration": {
                                    "container": "Python with Gunicorn",
                                    "cpu": "1 CPU",
                                    "memory": "512 MB",
                                    "scaling": "Auto-scaling from 1 to 2 instances",
                                    "environment_variables": {
                                        "CLOUD_RUN": "true",
                                        "POSTGRES_USER": "subscription_app_user",
                                        "POSTGRES_DB": "subscription_app",
                                        "INSTANCE_CONNECTION_NAME": "project:region:instance"
                                    },
                                    "secrets": {
                                        "POSTGRES_PASSWORD": "From Secret Manager"
                                    }
                                }
                            }
                        ]
                    },
                    "database": {
                        "service": "Cloud SQL",
                        "description": "Fully managed PostgreSQL database service",
                        "configuration": {
                            "type": "PostgreSQL",
                            "users": [
                                "subscription_app_user (read/write)",
                                "subscription_app_readonly (read-only)"
                            ],
                            "databases": ["subscription_app"]
                        },
                        "connection": "Backend connects via Cloud SQL Unix socket adapter"
                    },
                    "container_registry": {
                        "service": "Artifact Registry",
                        "description": "Storage for Docker container images",
                        "repositories": ["frontend and backend container images"]
                    },
                    "secrets": {
                        "service": "Secret Manager",
                        "description": "Secure storage for sensitive configuration",
                        "secrets": ["Database credentials"]
                    }
                },
                "deployment_workflow": [
                    "Build container images locally",
                    "Push images to Google Artifact Registry",
                    "Deploy backend service to Cloud Run with Cloud SQL connection",
                    "Deploy frontend service to Cloud Run with backend URL configuration",
                    "Configure service accounts with necessary permissions"
                ],
                "security": {
                    "service_accounts": "Dedicated service account for Cloud Run services",
                    "permissions": [
                        "Cloud SQL Client role for database access",
                        "Secret Manager Secret Accessor role for accessing secrets"
                    ]
                },
                "monitoring": {
                    "logs": "Standard output/error logs captured by Cloud Logging",
                    "metrics": "Cloud Run provides request count, latency, and instance metrics"
                }
            }
        }
        
        return {
            "status": "success",
            "message": "Application architecture information retrieved successfully",
            "result": result
        }
    except (RuntimeError, IOError) as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve application architecture information: {str(e)}",
            "result": {}
        }


def get_contact_information():
    """
    Get detailed contact information for the Dunder Mifflin Play application.
    
    This function returns a dictionary with contact information for various teams responsible
    for different aspects of the application, including development, operations, database
    administration, and support tiers.
    
    Returns:
        dict: A dictionary containing:
            - status (str): 'success' if information was retrieved successfully, 'error' otherwise
            - message (str): A message describing the result of the operation
            - result (dict): A dictionary with contact information organized by teams and roles
    """
    try:
        # Create the result dictionary with contact information
        result = {
            "development_teams": {
                "backend_team": {
                    "name": "Serpents",
                    "responsibilities": [
                        "Flask API development", 
                        "Database schema design", 
                        "Business logic implementation", 
                        "API performance optimization"
                    ],
                    "contact_channels": {
                        "slack": "#backend-dev",
                        "email": "backend-team@example.com",
                        "on_call": "PagerDuty schedule 'Backend On-Call'"
                    }
                },
                "frontend_team": {
                    "name": "Phoenix",
                    "responsibilities": [
                        "HTML/JS/CSS development", 
                        "User interface design", 
                        "API integration from the client-side"
                    ],
                    "contact_channels": {
                        "slack": "#frontend-dev",
                        "email": "frontend-team@example.com"
                    }
                }
            },
            "operations_and_infrastructure": {
                "infrastructure_team": {
                    "name": "Titans",
                    "responsibilities": [
                        "Google Cloud Platform administration",
                        "Cloud Run service management",
                        "Cloud SQL database administration", 
                        "Networking configuration", 
                        "Monitoring setup", 
                        "CI/CD pipeline management"
                    ],
                    "contact_channels": {
                        "slack": "#infra-ops",
                        "email": "infra-team@example.com",
                        "on_call": "PagerDuty schedule 'Infra On-Call'"
                    }
                },
                "dba_team": {
                    "name": "Part of Titans",
                    "responsibilities": [
                        "Database backups", 
                        "Performance tuning", 
                        "Schema migrations", 
                        "User access management"
                    ],
                    "contact_channels": {
                        "slack": "@db-admins in #infra-ops channel"
                    }
                }
            },
            "support_tiers": {
                "tier_1": {
                    "responsibilities": [
                        "Initial troubleshooting", 
                        "Ticket routing"
                    ],
                    "tools": "Uses runbooks based on documentation"
                },
                "tier_2": {
                    "responsibilities": [
                        "Application specialist support", 
                        "Liaison with development teams"
                    ],
                    "capabilities": [
                        "Log analysis", 
                        "Read-only database queries"
                    ]
                },
                "tier_3": {
                    "description": "Development and Infrastructure teams (as listed above)"
                }
            }
        }
        
        return {
            "status": "success",
            "message": "Contact information retrieved successfully",
            "result": result
        }
    except (RuntimeError, IOError) as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve contact information: {str(e)}",
            "result": {}
        }
