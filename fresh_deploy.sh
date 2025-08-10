#!/usr/bin/env bash
set -euo pipefail

# Change PROJECT if your compose project name isn't the current folder name.
PROJECT="${PROJECT:-$(basename "$PWD")}"
VOLUME="${VOLUME:-${PROJECT}_questionnaire_data}"

echo "Project: $PROJECT"
echo "Volume to remove: $VOLUME"

echo "Bringing stack down and deleting volumes…"
docker compose down -v

echo "Rebuilding images…"
docker compose build

echo "Starting stack…"
docker compose up -d

echo "Done. Containers:"
docker compose ps
