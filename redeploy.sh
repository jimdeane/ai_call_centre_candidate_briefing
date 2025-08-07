#!/bin/bash
echo "Stopping and removing old container..."
docker compose down

echo "Rebuilding and starting fresh..."
docker compose up --build -d

echo "✅ Questionnaire app deployed and running on http://localhost:5000"
