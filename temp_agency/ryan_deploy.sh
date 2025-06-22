#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
#  Cloud Run Deployment Script for Ryan Howard Agent
#  You've got this! 🚀
# ─────────────────────────────────────────────────────────────────────────────

# Usage:
#   ./ryan_deploy.sh [--skip-ci]
#
# Examples:
#   ./ryan_deploy.sh           # Deploy Ryan with build/push
#   ./ryan_deploy.sh --skip-ci # Deploy Ryan without building/pushing
#
# Required env vars:
#   PROJECT             — GCP project ID
#   REGION              — Cloud Run region (e.g. us-central1)
#   REPO                — Artifact Registry repo name
#   SERVICE_ACCOUNT     — name (without @) of the Cloud Run SA
#   CLOUDSQL_INSTANCE   — fully qualified Cloud SQL instance (proj:region:instance)
#   DATABASE_URL        — secret name in Secret Manager for database URL
#   ENVIRONMENT         — deployment environment (e.g. production)
#   TEMP_AGENCY_URL     — URL for the temp agency service (if applicable)
#   GOOGLE_API_KEY      — Secret name for Google API key
#   PUBLIC_PATHS        — Secret name for public paths configuration
#
# Optional env vars for Ryan-specific secrets:
#   RYAN_SECRET_CONFIG   — configuration secret for Ryan

# Parse command line arguments
SKIP_CI=false

# Check for skip-ci flag
if [[ "${1:-}" == "--skip-ci" ]]; then
  SKIP_CI=true
fi

for v in PROJECT REGION REPO SERVICE_ACCOUNT CLOUDSQL_INSTANCE DATABASE_URL ENVIRONMENT TEMP_AGENCY_URL GOOGLE_API_KEY PUBLIC_PATHS; do
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
echo "✅  Environment:        $ENVIRONMENT"
if [[ "$SKIP_CI" == "true" ]]; then
  echo "✅  CI Skip:            Skipping build and push of images"
fi
echo "🚀  Deploying Ryan Howard agent"

# Cloud Run flags for Ryan
CLOUD_RUN_FLAGS=(
  --region "$REGION"
  --service-account "$SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com"
  --add-cloudsql-instances "$CLOUDSQL_INSTANCE"
  --set-secrets "DATABASE_URL=${DATABASE_URL}:latest"
  --cpu "2"
  --memory "2048Mi"
  --min-instances "1"
  --max-instances "2"
  --port "8080"
  --allow-unauthenticated
  --set-secrets "TEMP_AGENCY_URL=${TEMP_AGENCY_URL}:latest,GOOGLE_API_KEY=${GOOGLE_API_KEY}:latest,PUBLIC_PATHS=${PUBLIC_PATHS}:latest"
)

# Environment variables for Ryan
ENV_VARS=(
  "ENVIRONMENT=$ENVIRONMENT"
  "GOOGLE_CLOUD_PROJECT=$PROJECT"
  "RUNTIME_PORT=8080"
  "GOOGLE_GENAI_USE_VERTEXAI=FALSE"
  "USER_ID=Venkat"
  "SECURE_AGENT=False"
  "MODEL_ID=gemini-2.0-flash"
  "AGENT_ID=ryan_howard"
  "AGENT_NAME=ryan_howard"
)

# Ryan's build context
AGENT_NAME="ryan-howard"
BUILD_CONTEXT="./ryan_howard"

# Generate timestamp for image tag (format: YYYYMMDD-HHMMSS)
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")

# Set up the image path with timestamp
image="$REGION-docker.pkg.dev/$PROJECT/$REPO/$AGENT_NAME:$TIMESTAMP"

# Build and push Ryan's image if not skipping CI
if [[ "$SKIP_CI" == "false" ]]; then
  echo
  echo "🔨  Building Ryan Howard image from $BUILD_CONTEXT with tag $TIMESTAMP..."
  docker build --platform linux/amd64 -t "$image" "$BUILD_CONTEXT"
  
  # Also tag it as latest for convenience
  docker tag "$image" "$REGION-docker.pkg.dev/$PROJECT/$REPO/$AGENT_NAME:latest"
  
  echo "📤  Pushing Ryan Howard images..."
  docker push "$image"
  docker push "$REGION-docker.pkg.dev/$PROJECT/$REPO/$AGENT_NAME:latest"
fi

# Ryan-specific secrets
agent_secrets=("AGENT_URL=ryan-howard-url:latest")

# Convert environment variables array to comma-separated string for --set-env-vars
env_vars_string=$(IFS=, ; echo "${ENV_VARS[*]}")

# Build deployment command
deploy_cmd=("gcloud" "run" "deploy" "$AGENT_NAME" "--image" "$image")

# Add flags
for flag in "${CLOUD_RUN_FLAGS[@]}"; do
  deploy_cmd+=("$flag")
done

# Add environment variables
deploy_cmd+=("--set-env-vars" "$env_vars_string")

# Add Ryan-specific secrets
for secret in "${agent_secrets[@]}"; do
  deploy_cmd+=("--set-secrets" "$secret")
done

echo "🚀  Deploying Ryan Howard to Cloud Run..."

# Echo the deploy command
echo "${deploy_cmd[*]}"

echo "-------------------------------------------------- \n"

# Execute the deploy command
"${deploy_cmd[@]}"

echo "-------------------------------------------------- \n"
echo "✅  Ryan Howard deployed successfully with image tag: $TIMESTAMP!"
echo "🎉  Deployment complete!"
