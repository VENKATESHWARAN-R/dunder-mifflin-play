#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
#  Cloud Run Deployment Script for Dunder Mifflin Agents
#  Here we go! 🚀
# ─────────────────────────────────────────────────────────────────────────────

# Usage:
#   ./agents_deploy.sh [--skip-ci]
#
# Examples:
#   ./agents_deploy.sh           # Deploy agents with build/push
#   ./agents_deploy.sh --skip-ci # Deploy agents without building/pushing
#
# Required env vars:
#   PROJECT             — GCP project ID (e.g. project-dunder-mifflin)
#   REGION              — Cloud Run region (e.g. europe-north1)
#   REPO                — Artifact Registry repo name (e.g. dunder-mifflin-repo)
#   SERVICE_ACCOUNT     — name (without @) of the Cloud Run SA (e.g. dunder-mifflin-sa)
#   CLOUDSQL_INSTANCE   — fully qualified Cloud SQL instance (proj:region:instance)
#   DATABASE_URL        — secret name in Secret Manager for database URL
#   GITHUB_PAT_TOKEN    — secret name for GitHub PAT token
#   GOOGLE_API_KEY      — Secret name for Google API key
#   MCP_SERVER_URL      — Secret name for MCP server URL
#   APP_DATABASE_URL    — Secret name for app database read-only URL
#

# Parse command line arguments
SKIP_CI=false

# Check for skip-ci flag
if [[ "${1:-}" == "--skip-ci" ]]; then
  SKIP_CI=true
fi

# Check required environment variables
for v in PROJECT REGION REPO SERVICE_ACCOUNT CLOUDSQL_INSTANCE DATABASE_URL GITHUB_PAT_TOKEN GOOGLE_API_KEY MCP_SERVER_URL APP_DATABASE_URL; do
  if [[ -z "${!v:-}" ]]; then
    echo "❌  Error: \$${v} is not set."
    exit 1
  fi
done

echo "✅  Project:            $PROJECT"
echo "✅  Region:             $REGION"
echo "✅  Repo:               $REPO"
echo "✅  Service Account:    $SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com"
echo "✅  Cloud SQL Instance: $CLOUDSQL_INSTANCE"
if [[ "$SKIP_CI" == "true" ]]; then
  echo "✅  CI Skip:            Skipping build and push of images"
fi
echo "🚀  Deploying Dunder Mifflin Agents"

# Cloud Run flags for Agents
CLOUD_RUN_FLAGS=(
  --region "$REGION"
  --service-account "$SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com"
  --add-cloudsql-instances "$CLOUDSQL_INSTANCE"
  --cpu "1"
  --memory "512Mi"
  --min-instances "1"
  --max-instances "2"
  --port "8080"
  --allow-unauthenticated
)

# Environment variables for Agents
ENV_VARS=(
  "HOLLY_MODEL_ID=gemini-2.5-flash-lite-preview-06-17"
  "ANGEL_MODEL_ID=gemini-2.5-flash-lite-preview-06-17"
  "DWIGHT_MODEL_ID=gemini-2.0-flash"
  "GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/"
  "ARTIFACT_SERVICE_URI=gs://dunder-mifflin-bucket"
  "TRACE_TO_CLOUD=true"
  "GOOGLE_GENAI_USE_VERTEXAI=FALSE"
)

# Secrets for Agents
SECRETS=(
  "GOOGLE_API_KEY=${GOOGLE_API_KEY}:latest"
  "GITHUB_PAT_TOKEN=${GITHUB_PAT_TOKEN}:latest"
  "DATABASE_URL=${DATABASE_URL}:latest"
  "MCP_SERVER_URL=${MCP_SERVER_URL}:latest"
  "APP_DATABASE_URL=${APP_DATABASE_URL}:latest"
)

# Agent's build context
SERVICE_NAME="dunder-mifflin-agents"
BUILD_CONTEXT="."

# Generate timestamp for image tag (format: YYYYMMDD-HHMMSS)
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")

# Set up the image path with timestamp
image="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE_NAME:latest.$(date "+%m.%d")"

# Build and push Agent's image if not skipping CI
if [[ "$SKIP_CI" == "false" ]]; then
  echo
  echo "🔨  Building Dunder Mifflin Agents image from $BUILD_CONTEXT with tag latest.$(date "+%m.%d")..."
  docker build --platform linux/amd64 -t "$image" "$BUILD_CONTEXT"
  
  echo "📤  Pushing Dunder Mifflin Agents image..."
  docker push "$image"
fi

# Convert environment variables array to comma-separated string for --set-env-vars
env_vars_string=$(IFS=, ; echo "${ENV_VARS[*]}")

# Build deployment command
deploy_cmd=("gcloud" "run" "deploy" "$SERVICE_NAME" "--image" "$image")

# Add flags
for flag in "${CLOUD_RUN_FLAGS[@]}"; do
  deploy_cmd+=("$flag")
done

# Add environment variables
deploy_cmd+=("--set-env-vars" "$env_vars_string")

# Add Secrets
secrets_string=$(IFS=, ; echo "${SECRETS[*]}")
deploy_cmd+=("--set-secrets" "$secrets_string")

echo "🚀  Deploying Dunder Mifflin Agents to Cloud Run..."

# Echo the deploy command
echo "${deploy_cmd[*]}"

echo "-------------------------------------------------- \n"

# Execute the deploy command
"${deploy_cmd[@]}"

echo "-------------------------------------------------- \n"
echo "✅  Dunder Mifflin Agents deployed successfully!"
echo "🎉  Deployment complete!"
