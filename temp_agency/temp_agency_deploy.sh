#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
#  Cloud Run Deployment Script for Dunder-Mifflin Temp Agency Service
#  You've got this! 🚀
# ─────────────────────────────────────────────────────────────────────────────

# Usage:
#   ./temp_agency_deploy.sh [--skip-ci]
#
# Examples:
#   ./temp_agency_deploy.sh                # Deploy temp-agency
#   ./temp_agency_deploy.sh --skip-ci      # Deploy temp-agency without building/pushing
#
# Required env vars:
#   PROJECT             — GCP project ID
#   REGION              — Cloud Run region (e.g. us-central1)
#   REPO                — Artifact Registry repo name
#   SERVICE_ACCOUNT     — name (without @) of the Cloud Run SA
#   CLOUDSQL_INSTANCE   — fully qualified Cloud SQL instance (proj:region:instance)
#   TEMP_AGENCY_DB_URL  — secret name in Secret Manager for temp-agency database URL
#   ENVIRONMENT         — deployment environment (e.g. production)
#

# Parse command line arguments
SKIP_CI=false

for arg in "$@"; do
  if [[ "$arg" == "--skip-ci" ]]; then
    SKIP_CI=true
  fi
done

for v in PROJECT REGION REPO SERVICE_ACCOUNT CLOUDSQL_INSTANCE TEMP_AGENCY_DB_URL ENVIRONMENT; do
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
  echo "✅  CI Skip:            Skipping build and push of image"
fi

# Define service details
SERVICE_NAME="temp-agency"
CONTEXT_PATH="./app"
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE_NAME:latest"

# Common Cloud Run flags for temp-agency
TEMP_AGENCY_FLAGS=(
  --region "$REGION"
  --service-account "$SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com"
  --add-cloudsql-instances "$CLOUDSQL_INSTANCE"
  --set-secrets "DATABASE_URL=${TEMP_AGENCY_DB_URL}:latest"
  --cpu "1"
  --memory "512Mi"
  --min-instances "1"
  --max-instances "2"
  --port "8080"
  --allow-unauthenticated
)

# Build and push images if not skipping CI
if [[ "$SKIP_CI" == "false" ]]; then
  echo
  echo "🔨  Building $SERVICE_NAME image from $CONTEXT_PATH..."
  docker build --platform linux/amd64 -t "$IMAGE" "$CONTEXT_PATH"
  echo "📤  Pushing $SERVICE_NAME image..."
  docker push "$IMAGE"
fi

# Define specific environment variables for temp-agency
ENV_VARS=(
  "--set-env-vars" "ENVIRONMENT=$ENVIRONMENT,PUBLIC_AGENT_CARD_PATH=/.well-known/agent.json,RUNTIME_PORT=8080"
)

echo "🚀  Deploying $SERVICE_NAME to Cloud Run..."

echo "gcloud run deploy $SERVICE_NAME --image $IMAGE ${TEMP_AGENCY_FLAGS[*]} ${ENV_VARS[*]}"
echo "-------------------------------------------------- \n"

# gcloud run deploy "$SERVICE_NAME" \
#    --image "$IMAGE" \
#    "${TEMP_AGENCY_FLAGS[@]}" \
#    "${ENV_VARS[@]}"

echo "-------------------------------------------------- \n"
echo "✅  $SERVICE_NAME deployed successfully!"
echo "-------------------------------------------------- \n"

echo "🎉  Temp Agency deployment completed!"
